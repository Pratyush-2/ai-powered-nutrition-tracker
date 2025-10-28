import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nutrition_app/screens/log_food_screen.dart';

void main() {
  testWidgets('LogFoodScreen has a barcode scanner button', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: LogFoodScreen(userId: 1),
    ));

    // Find the barcode scanner button
    final barcodeButton = find.byIcon(Icons.qr_code_scanner);
    expect(barcodeButton, findsOneWidget);
  });
}
