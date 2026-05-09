// SPDX-License-Identifier: AGPL-3.0-or-later
// Part of {{ cookiecutter.public_service_name }} (PublicStack).
//
// Sealed event hierarchy. Apps publish events on the bus when service-
// layer mutations succeed; widgets subscribe and invalidate Riverpod
// providers on matching event types. Avoid emitting from UI code —
// keep emit calls in service success branches.

sealed class AppEvent {
  const AppEvent();
}

/// Item placeholder events. Replace with real domain events.
sealed class ItemEvent extends AppEvent {
  const ItemEvent();
}

class ItemCreated extends ItemEvent {
  const ItemCreated(this.itemId, this.name);
  final String itemId;
  final String name;
}

class ItemDeleted extends ItemEvent {
  const ItemDeleted(this.itemId);
  final String itemId;
}

/// Generic mutation-failure event. Subscribe in a global listener to
/// surface a snackbar with copy keyed off `code`.
class MutationFailed extends AppEvent {
  const MutationFailed({required this.code, required this.message});
  final String code;
  final String message;
}
