import 'dart:io';
import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:government_assistant/custom_widgets/toast_bar.dart';
import 'package:government_assistant/model/user_model.dart';
import 'package:government_assistant/shared_preferences.dart';
import 'package:government_assistant/utils/utils.dart';

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

  // Rejestracja z e-mailem i hasłem
  Future<void> signUpWithEmailPassword(BuildContext context, String email,
      String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      UserCredential userCredential = await _firebaseAuth
          .createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      _uid = userCredential.user?.uid;
      await saveUserDataToFirebase(context, email);
      _isLoading = false;
      notifyListeners();
    } on FirebaseAuthException catch (e) {
      toastBar(context, e.message.toString());
      _isLoading = false;
      notifyListeners();
    }
  }

  // Logowanie z e-mailem i hasłem
  Future<void> signInWithEmailPassword(BuildContext context, String email,
      String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      UserCredential userCredential = await _firebaseAuth
          .signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      _uid = userCredential.user?.uid;
      await getDataFromFirestore();
      setSignedInStatus();
      _isLoading = false;
      notifyListeners();
    } on FirebaseAuthException catch (e) {
      toastBar(context, e.message.toString());
      _isLoading = false;
      notifyListeners();
    }
  }

  // Logowanie przez Google
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

  // Logowanie przez Facebook
  Future<void> signInWithFacebook(BuildContext context) async {
    _isLoading = true;
    notifyListeners();
    try {
      final LoginResult loginResult = await FacebookAuth.instance.login();
      final AccessToken accessToken = loginResult.accessToken!;

      final AuthCredential credential = FacebookAuthProvider.credential(
          accessToken.token);
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

  // Zapisanie danych użytkownika do Firestore
  void saveUserDataToFirebase(BuildContext context, String email) async {
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
        // Możesz ustawić domyślną ikonę, jeśli nie ma zdjęcia
        phoneNumber: '', // Pusty, bo nie używamy telefonu
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

  // Pobranie danych użytkownika z Firestore
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

  // Wylogowanie użytkownika
  Future<void> userSignOut() async {
    SharedPreferences s = await SharedPreferences.getInstance();
    await _firebaseAuth.signOut();
    _isSignedIn = false;
    notifyListeners();
    s.clear();
  }
}
