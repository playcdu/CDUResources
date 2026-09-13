// Reflection names below come from the exact official mappings in the audit manifest.
// Checks released-client parser code only: it does NOT load textures into OpenGL.
import com.google.gson.*;
import com.mojang.serialization.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.*;

public class CheckTargetCodecs {
    static JsonObject object(ZipFile zip, String name) throws Exception {
        return JsonParser.parseString(new String(zip.getInputStream(zip.getEntry(name)).readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject();
    }
    static Object codec(String name, JsonObject json) throws Exception {
        Class<?> type=Class.forName(name);
        Field field=type.getDeclaredField("a");field.setAccessible(true);
        Object c=field.get(null);
        Codec<?> codec=c instanceof MapCodec<?> m?m.codec():(Codec<?>)c;
        DataResult<?> result=codec.parse(JsonOps.INSTANCE,json);
        if (result.error().isPresent()) throw new IllegalStateException(name+": "+result);
        return result.result().orElseThrow();
    }
    static Object legacy(String name, String method, boolean instance, JsonObject json) throws Exception {
        Class<?> type=Class.forName(name);
        Method m=type.getDeclaredMethod(method,JsonObject.class);m.setAccessible(true);
        return m.invoke(instance?type.getDeclaredConstructor().newInstance():null,json);
    }
    public static void main(String[] args) throws Exception {
        String version=args[0];boolean old=version.equals("1.19.2");
        String bitmap=old?"ejn$a":version.equals("1.20.1")?"erw$a":"flm$a";
        String spacing=old?"dyv":version.equals("1.20.1")?"ego$a":"ezo$a";
        try(ZipFile zip=new ZipFile(args[1])) {
            int bitmapCount=0,spaceCount=0;
            for(JsonElement e:object(zip,"assets/quasar_gui/font/menu.json").getAsJsonArray("providers")) {
                JsonObject p=e.getAsJsonObject();boolean b=p.get("type").getAsString().equals("bitmap");
                if(old)legacy(b?bitmap:spacing,"a",false,p);else codec(b?bitmap:spacing,p);
                if(b)bitmapCount++;else spaceCount++;
            }
            JsonObject pack=object(zip,"pack.mcmeta").getAsJsonObject("pack");
            System.out.printf("%s: %d bitmap providers and %d space provider parsed by released client code.%n",version,bitmapCount,spaceCount);
            if(old)legacy("ahr","b",true,pack);
            else if(version.equals("1.20.1"))legacy("aka","b",true,pack);
            else {
                Class.forName("ab").getMethod("a").invoke(null);
                Class.forName("akt").getMethod("a").invoke(null);
                codec("atf",pack);
            }
            System.out.printf("%s: %d bitmap providers, %d space provider and root metadata parsed by released client code. Texture loading/rendering NOT tested.%n",version,bitmapCount,spaceCount);
        }
    }
}
