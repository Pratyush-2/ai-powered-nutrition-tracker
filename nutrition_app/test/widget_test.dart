import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nutrition_app/screens/main_tabs.dart';

void main() {
  testWidgets('MainTabs has a BottomNavigationBar with 5 items', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: MainTabs(userId: 1),
    ));

    // Find the BottomNavigationBar
    final bottomNavBar = find.byType(BottomNavigationBar);
    expect(bottomNavBar, findsOneWidget);

    // Check for 5 items
    expect(find.byIcon(Icons.home), findsOneWidget);
    expect(find.byIcon(Icons.history), findsOneWidget);
    expect(find.byIcon(Icons.chat_bubble_outline), findsOneWidget);
    expect(find.byIcon(Icons.flag), findsOneWidget);
    expect(find.byIcon(Icons.person), findsOneWidget);
  });
}