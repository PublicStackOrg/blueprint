// SPDX-License-Identifier: AGPL-3.0-or-later

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kiosk/features/home/kiosk_home_screen.dart';
import 'package:ui/ui.dart';

class _FakeApiClient extends ApiClient {
  _FakeApiClient() : super(baseUrl: 'http://test');
}

void main() {
  testWidgets('shows welcome screen with start button', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(_FakeApiClient()),
        ],
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
