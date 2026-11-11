#!/usr/bin/env python3
"""Temporary source compatibility bridge for FTB Teams feature/26.3.

Run on the checked-out upstream FTB-Teams tree in GitHub Actions.
No upstream FTB files are modified on GitHub by this script.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_ftb-teams")
pkg = root / "common/src/main/java/dev/ftb/mods/ftbteams/api/property"

replacements = {
    "StringSetProperty.java": [
        ("new HashSet<>(buf.readList(b -> b.readUtf(Short.MAX_VALUE)))",
         "new HashSet<>(NetworkCollections.readStringList(buf))"),
        ("buf.writeCollection(getDefaultValue(), FriendlyByteBuf::writeUtf);",
         "NetworkCollections.writeStringCollection(buf, getDefaultValue());"),
        ("buf.writeCollection(value, FriendlyByteBuf::writeUtf);",
         "NetworkCollections.writeStringCollection(buf, value);"),
        ("return buf.readCollection(HashSet::new, FriendlyByteBuf::readUtf);",
         "return new HashSet<>(NetworkCollections.readStringList(buf));"),
    ],
    "StringMapProperty.java": [
        ("buf.writeMap(getDefaultValue(), FriendlyByteBuf::writeUtf, toNet::accept);",
         "NetworkCollections.writeMap(buf, getDefaultValue(), toNet);"),
        ("buf.writeMap(value, FriendlyByteBuf::writeUtf, toNet::accept);",
         "NetworkCollections.writeMap(buf, value, toNet);"),
        ("return buf.readMap(FriendlyByteBuf::readUtf, fromNet::apply);",
         "return NetworkCollections.readMap(buf, fromNet);"),
    ],
    "EnumProperty.java": [
        ("buf.readList(b -> b.readUtf(Short.MAX_VALUE))",
         "NetworkCollections.readStringList(buf)"),
        ("buf.writeCollection(values, FriendlyByteBuf::writeUtf);",
         "NetworkCollections.writeStringCollection(buf, values);"),
    ],
    "StringListProperty.java": [
        ("buf.readList(b -> b.readUtf(Short.MAX_VALUE))",
         "NetworkCollections.readStringList(buf)"),
        ("buf.writeCollection(getDefaultValue(), FriendlyByteBuf::writeUtf);",
         "NetworkCollections.writeStringCollection(buf, getDefaultValue());"),
        ("buf.writeCollection(value, FriendlyByteBuf::writeUtf);",
         "NetworkCollections.writeStringCollection(buf, value);"),
        ("return buf.readList(FriendlyByteBuf::readUtf);",
         "return NetworkCollections.readStringList(buf);"),
    ],
}

for filename, rules in replacements.items():
    path = pkg / filename
    source = path.read_text()
    for before, after in rules:
        if before not in source:
            raise SystemExit(f"Missing expected upstream pattern: {filename}: {before}")
        source = source.replace(before, after)
    path.write_text(source)
    print("Patched", path)

helper = pkg / "NetworkCollections.java"
helper.write_text("""package dev.ftb.mods.ftbteams.api.property;

import net.minecraft.network.FriendlyByteBuf;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.Function;

/** Small compatibility adapter for collection methods removed from FriendlyByteBuf in MC 26.3. */
final class NetworkCollections {
    private static final int MAX_ENTRIES = 65535;

    private NetworkCollections() {}

    private static int readSize(FriendlyByteBuf buf) {
        int size = buf.readVarInt();
        if (size < 0 || size > MAX_ENTRIES) {
            throw new IllegalArgumentException("Invalid collection size: " + size);
        }
        return size;
    }

    static List<String> readStringList(FriendlyByteBuf buf) {
        int count = readSize(buf);
        List<String> strings = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            strings.add(buf.readUtf(Short.MAX_VALUE));
        }
        return strings;
    }

    static void writeStringCollection(FriendlyByteBuf buf, Collection<String> values) {
        if (values.size() > MAX_ENTRIES) {
            throw new IllegalArgumentException("Collection too large");
        }
        buf.writeVarInt(values.size());
        for (String value : values) {
            buf.writeUtf(value, Short.MAX_VALUE);
        }
    }

    static <T> Map<String,T> readMap(FriendlyByteBuf buf, Function<FriendlyByteBuf,T> valueReader) {
        int count = readSize(buf);
        Map<String,T> result = new HashMap<>();
        for (int i = 0; i < count; i++) {
            result.put(buf.readUtf(Short.MAX_VALUE), valueReader.apply(buf));
        }
        return result;
    }

    static <T> void writeMap(FriendlyByteBuf buf, Map<String,T> values, BiConsumer<FriendlyByteBuf,T> valueWriter) {
        if (values.size() > MAX_ENTRIES) {
            throw new IllegalArgumentException("Map too large");
        }
        buf.writeVarInt(values.size());
        values.forEach((key, value) -> {
            buf.writeUtf(key, Short.MAX_VALUE);
            valueWriter.accept(buf, value);
        });
    }
}
""")
print("Added", helper)
