// Headless verification using the official released Minecraft 26.1.2 codecs.
import com.google.gson.*;
import com.mojang.serialization.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.zip.*;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.metadata.pack.PackFormat;
import net.minecraft.client.gui.font.providers.GlyphProviderDefinition;
import net.minecraft.client.renderer.item.ItemModels;

public class Check26Pack {
    static JsonElement read(ZipFile z, String path) throws Exception {
        return JsonParser.parseString(new String(z.getInputStream(z.getEntry(path)).readAllBytes(), StandardCharsets.UTF_8));
    }
    static void require(DataResult<?> result,String name) {
        if(result.error().isPresent())throw new IllegalStateException(name+": "+result.error().get().message());
    }
    public static void main(String[] args) throws Exception {
        try(ZipFile z=new ZipFile(args[0])) {
            var pack=read(z,"pack.mcmeta").getAsJsonObject().getAsJsonObject("pack");
            var format=PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE,pack);
            require(format,"pack metadata");
            if(!format.result().orElseThrow().isValueInRange(PackFormat.of(84)))throw new IllegalStateException("format84 excluded");
            int count=0;
            for(var provider:read(z,"assets/quasar_gui/font/menu.json").getAsJsonObject().getAsJsonArray("providers")) {
                require(GlyphProviderDefinition.MAP_CODEC.codec().parse(JsonOps.INSTANCE,provider),"font provider"+(count++));
            }
            ItemModels.bootstrap();
            var model=read(z,"assets/quasar_gui/items/button_carrier.json").getAsJsonObject().get("model");
            require(ItemModels.CODEC.parse(JsonOps.INSTANCE,model),"carrier model");
            if(z.getEntry("assets/minecraft/models/item/paper.json")!=null)throw new IllegalStateException("old vanilla override remains");
            System.out.println("PASS released26.1.2: pack format84, "+count+" font providers, minecraft:empty item carrier, no vanilla paper override");
        }
    }
}
