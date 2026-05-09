// SPDX-License-Identifier: AGPL-3.0-or-later

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:resident/features/home/home_screen.dart';
import 'package:ui/ui.dart';

/// Test client that returns canned responses without touching the network.
class _FakeApiClient extends ApiClient {
  _FakeApiClient() : super(baseUrl: 'http://test');

  @override
  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? query}) async {
    if (path == '/health') {
      return Response<T>(
        requestOptions: RequestOptions(path: path),
        data: <String, dynamic>{'status': 'ok'} as T,
        statusCode: 200,
      );
    }
    throw UnimplementedError('fake client missing handler for $path');
  }
}

void main() {
  testWidgets('renders welcome banner', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(_FakeApiClient()),
        ],
        child: MaterialApp(
          theme: buildAppTheme(),
          home: const HomeScreen(),
        ),
      ),
    );

    expect(find.textContaining('Welcome to'), findsOneWidget);

    // Let the canned health response resolve so no timers leak past
    // the test boundary.
    await tester.pumpAndSettle();
  });
}
