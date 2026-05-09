// SPDX-License-Identifier: AGPL-3.0-or-later

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kiosk/features/home/kiosk_home_screen.dart';
import 'package:ui/ui.dart';

void main() {
  testWidgets('shows welcome screen with start button', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: buildAppTheme(),
          home: const KioskHomeScreen(),
        ),
      ),
    );

    expect(find.text('Welcome'), findsOneWidget);
    expect(find.text('Start'), findsOneWidget);
  });
}
