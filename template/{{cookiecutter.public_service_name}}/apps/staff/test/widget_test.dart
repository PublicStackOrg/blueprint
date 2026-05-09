// SPDX-License-Identifier: AGPL-3.0-or-later

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:staff/features/home/staff_home_screen.dart';
import 'package:ui/ui.dart';

class _FakeApiClient extends ApiClient {
  _FakeApiClient() : super(baseUrl: 'http://test');
}

void main() {
  testWidgets('renders staff dashboard heading', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(_FakeApiClient()),
        ],
        child: MaterialApp(
          theme: buildAppTheme(),
          home: const StaffHomeScreen(),
        ),
      ),
    );

    expect(find.text('Staff dashboard'), findsOneWidget);
  });
}
