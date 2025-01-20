import 'package:flutter/material.dart';

void toastBar(BuildContext context, String title) {
  BottomAppBar bottomAppBar = BottomAppBar(
    color: const Color(0xFF0A0A0A),
    child: Container(
      decoration: BoxDecoration(
        color: const Color.fromRGBO(27, 27, 27, 1),
        borderRadius: BorderRadius.circular(14.0), // Set border radius here
      ),
      margin: const EdgeInsets.only(bottom: 21.0, left: 24.0, right: 25.0),
      height: 50.0,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text(title,
              style: const TextStyle(
                  fontSize: 18.0,
                  fontFamily: 'Poppins',
                  fontWeight: FontWeight.w500,
                  color: Color.fromRGBO(119, 119, 119, 1))),
        ],
      ),
    ),
  );

  Scaffold.of(context).showBottomSheet((context) => bottomAppBar);

  Future.delayed(const Duration(seconds: 3), () {
    Navigator.of(context).pop();
  });
}