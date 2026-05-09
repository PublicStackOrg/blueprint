// SPDX-License-Identifier: AGPL-3.0-or-later
// Part of {{ cookiecutter.public_service_name }} (PublicStack).
//
// Riverpod-backed event bus. The bus is a `StreamController.broadcast`,
// exposed via two providers: one for the bus itself (used to emit), one
// for the stream (used to listen).

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'event.dart';

class AppEventBus {
  AppEventBus() : _controller = StreamController<AppEvent>.broadcast();

  final StreamController<AppEvent> _controller;

  Stream<AppEvent> get stream => _controller.stream;

  void emit(AppEvent event) {
    _controller.add(event);
  }

  void dispose() {
    _controller.close();
  }
}

final appEventBusProvider = Provider<AppEventBus>((ref) {
  final bus = AppEventBus();
  ref.onDispose(bus.dispose);
  return bus;
});

final appEventStreamProvider = StreamProvider<AppEvent>((ref) {
  final bus = ref.watch(appEventBusProvider);
  return bus.stream;
});
