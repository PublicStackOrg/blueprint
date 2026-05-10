import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:{{ cookiecutter.app_name }}/main.dart';

void main() {
  testWidgets('renders app title', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: App()));
    expect(find.text('{{ cookiecutter.app_name }}'), findsWidgets);
  });
}
