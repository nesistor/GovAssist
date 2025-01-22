import 'dart:io';
import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:government_assistant/components/toast_bar.dart';
import 'package:government_assistant/models/user_model.dart';
import 'package:government_assistant/shared_preferences.dart';
import 'package:government_assistant/utils/utils.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_facebook_auth/flutter_facebook_auth.dart';

import 'package:government_assistant/pages//chat_page/chat_page.dart';


class AuthProvider extends ChangeNotifier {
  bool _isSignedIn = false;

  bool get isSignedIn => _isSignedIn;
  bool _isLoading = false;

  bool get isLoading => _isLoading;
  String? _uid;

  String get uid => _uid!;
  UserModel? _userModel;

  UserModel get userModel => _userModel!;

  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final FirebaseFirestore _firebaseFirestore = FirebaseFirestore.instance;
  final FirebaseStorage _firebaseStorage = FirebaseStorage.instance;

  AuthProvider() {
    checkSignedInStatus();
  }

  Future<void> checkSignedInStatus() async {
    SharedPreferencesHelper.checkSignedIn((isSignedIn) {
      _isSignedIn = isSignedIn;
      notifyListeners();
    });
  }

  Future<void> setSignedInStatus() async {
    await SharedPreferencesHelper.setSignIn(true);
    _isSignedIn = true;
    notifyListeners();
  }

  Future<String?> getUserToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      User? user = _firebaseAuth.currentUser;
      if (user != null) {
        IdTokenResult tokenResult = await user.getIdTokenResult();
        String token = tokenResult.token ?? "";
        await SharedPreferencesHelper.saveUserToken(token);
        return tokenResult.token;
      }
    } catch (e) {
      print("Error getting user token: $e");
    }
    return null;
  }

  Future<void> signUpWithEmailPassword(BuildContext context, String email,
      String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      // Check if email is already in use
      if (await isEmailRegistered(email)) {
        throw FirebaseAuthException(
            code: 'email-already-in-use', message: 'Email is already in use');
      }

      UserCredential userCredential = await _firebaseAuth
          .createUserWithEmailAndPassword(email: email, password: password);
      _uid = userCredential.user?.uid;
      await saveUserDataToFirebase(context, email);
      setSignedInStatus();
    } on FirebaseAuthException catch (e) {
      toastBar(context, e.message.toString());
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signInWithEmailPassword(BuildContext context, String email,
      String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      UserCredential userCredential = await _firebaseAuth
          .signInWithEmailAndPassword(email: email, password: password);
      _uid = userCredential.user?.uid;
      await getDataFromFirestore();
      setSignedInStatus();

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => ChatPage()),
      );
    } on FirebaseAuthException catch (e) {
      toastBar(context, e.message.toString());
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }


  Future<void> signInWithGoogle(BuildContext context) async {
    _isLoading = true;
    notifyListeners();
    try {
      final GoogleSignIn googleSignIn = GoogleSignIn();
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      final GoogleSignInAuthentication googleAuth = await googleUser!
          .authentication;

      final AuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      UserCredential userCredential = await _firebaseAuth.signInWithCredential(
          credential);
      _uid = userCredential.user?.uid;
      await getDataFromFirestore();
      setSignedInStatus();

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      toastBar(context, e.toString());
      _isLoading = false;
      notifyListeners();
    }
  }

  //Future<void> signInWithFacebook(BuildContext context) async {
  //  _isLoading = true;
  //  notifyListeners();
  //  try {
  //    final LoginResult loginResult = await FacebookAuth.instance.login();
  //    final AccessToken accessToken = loginResult.accessToken!;

  // Use `accessToken.token` instead of `accessToken.value`
  //    final AuthCredential credential = FacebookAuthProvider.credential(
  //        accessToken.token);

  //    UserCredential userCredential = await _firebaseAuth.signInWithCredential(
  //        credential);
  //    _uid = userCredential.user?.uid;
  //    await getDataFromFirestore();
  //    setSignedInStatus();

  //    _isLoading = false;
  //    notifyListeners();
  //  } catch (e) {
  //    toastBar(context, e.toString());
  //    _isLoading = false;
  //    notifyListeners();
  //  }
  //}


  Future<void> saveUserDataToFirebase(BuildContext context,
      String email) async {
    _isLoading = true;
    notifyListeners();
    try {
      UserModel userModel = UserModel(
        uid: _uid!,
        email: email,
        createdAt: DateTime
            .now()
            .millisecondsSinceEpoch
            .toString(),
        profilePic: '',
        phoneNumber: '',
        bio: '',
        name: '',
      );
      _userModel = userModel;

      await _firebaseFirestore
          .collection("users")
          .doc(_uid)
          .set(userModel.toMap())
          .then((value) {
        _isLoading = false;
        notifyListeners();
      });
    } on FirebaseAuthException catch (e) {
      toastBar(context, e.message.toString());
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> getDataFromFirestore() async {
    await _firebaseFirestore
        .collection("users")
        .doc(_firebaseAuth.currentUser!.uid)
        .get()
        .then((DocumentSnapshot snapshot) {
      _userModel = UserModel(
        name: snapshot['name'],
        email: snapshot['email'],
        createdAt: snapshot['createdAt'],
        bio: snapshot['bio'],
        uid: snapshot['uid'],
        profilePic: snapshot['profilePic'],
        phoneNumber: snapshot['phoneNumber'],
      );
      _uid = userModel.uid;
    });
  }

  Future<void> userSignOut() async {
    SharedPreferences s = await SharedPreferences.getInstance();
    await _firebaseAuth.signOut();
    _isSignedIn = false;
    notifyListeners();
    s.clear();
  }
}

Future<bool> isEmailRegistered(String email) async {
  final List<String> signInMethods =
  await FirebaseAuth.instance.fetchSignInMethodsForEmail(email);
  return signInMethods.isNotEmpty;
}

