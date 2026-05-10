// SPDX-License-Identifier: AGPL-3.0-or-later

import 'package:flutter_test/flutter_test.dart';
import 'package:ui/ui.dart';

void main() {
  test('AppEventBus delivers emitted events to listeners', () async {
    final bus = AppEventBus();
    final received = <AppEvent>[];
    final sub = bus.stream.listen(received.add);

    bus.emit(const ItemCreated('id-1', 'first'));
    bus.emit(const ItemDeleted('id-1'));

    await Future<void>.delayed(Duration.zero);

    expect(received.length, 2);
    expect(received[0], isA<ItemCreated>());
    expect(received[1], isA<ItemDeleted>());

    await sub.cancel();
    bus.dispose();
  });
}
