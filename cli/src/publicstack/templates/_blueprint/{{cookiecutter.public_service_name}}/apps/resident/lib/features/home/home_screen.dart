// SPDX-License-Identifier: AGPL-3.0-or-later
// Part of {{ cookiecutter.public_service_name }} (PublicStack).

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ui/ui.dart';

final healthProvider = FutureProvider<String>((ref) async {
  final client = ref.watch(apiClientProvider);
  final response = await client.get<Map<String, dynamic>>('/health');
  return response.data?['status'] as String? ?? 'unknown';
});

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final health = ref.watch(healthProvider);
    return AppScaffold(
      title: '{{ cookiecutter.public_service_name }}',
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome to {{ cookiecutter.public_service_name }}',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: AppSpacing.md),
            health.when(
              data: (status) => Text(
                '{{ cookiecutter.public_service_name }} is $status',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              loading: () => const LoadingIndicator(label: 'Checking service health'),
              error: (err, _) => Text(
                'API unreachable: $err',
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: AppColors.error),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            AppButton(
              label: 'Refresh',
              onPressed: () => ref.invalidate(healthProvider),
            ),
          ],
        ),
      ),
    );
  }
}
