// SPDX-License-Identifier: AGPL-3.0-or-later
// Part of {{ cookiecutter.public_service_name }} (PublicStack).
//
// Accessibility helpers. Civic software has to meet WCAG 2.2 AA;
// the compliance suite (Phase 5) will enforce the major checks.
// These helpers are the easy primitives apps reach for.

import 'package:flutter/material.dart';

/// Wraps a widget with a semantic label. Use when a widget's visual
/// content alone doesn't convey its purpose to a screen reader (icons,
/// status indicators, badges).
Widget labelled({required String label, required Widget child}) {
  return Semantics(label: label, child: child);
}

/// Announces `message` to assistive technologies. Useful after a
/// successful mutation when there is no visible UI confirmation.
void announce(BuildContext context, String message) {
  SemanticsService.announce(message, Directionality.of(context));
}
