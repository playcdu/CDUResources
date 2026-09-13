// Executes released 26.2 pack-format codec without starting Minecraft or OpenGL.
// Run with the official client JAR and its launcher-declared library dependencies.
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import java.nio.file.Files;
import java.nio.file.Path;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.metadata.pack.PackFormat;

public class CheckReleasedMetadata {
    public static void main(String[] args) throws Exception {
        JsonObject root = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonObject pack = root.getAsJsonObject("pack");
        System.out.println("Shipped metadata: " + PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE, pack));
        pack.addProperty("pack_format", 9);
        System.out.println("Rejected candidate pack_format9: " + PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE, pack));
        pack.addProperty("pack_format", 15);
        System.out.println("Candidate pack_format15, same range: " + PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE, pack));
        pack.addProperty("min_format", 9);
        pack.addProperty("max_format", 34);
        System.out.println("Candidate format15 plus min/max9..34: " + PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE, pack));
    }
}
