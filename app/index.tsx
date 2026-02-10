import { Text, View } from "react-native";
import { useFonts } from "expo-font";

export default function Page() {
  let [fontsLoaded] = useFonts({
    "Geist-Regular": require("../assets/fonts/Geist-Regular.ttf"),
    "Geist-Medium": require("../assets/fonts/Geist-Medium.ttf"),
    "Geist-SemiBold": require("../assets/fonts/Geist-SemiBold.ttf"),
    "Geist-Bold": require("../assets/fonts/Geist-Bold.ttf"),
    "Geist-Black": require("../assets/fonts/Geist-Black.ttf"),
  });
  if (!fontsLoaded) {
    return null;
  }
  return (
    <View className="flex-1 bg-black ">
      <View className="flex-1 w-full max-w-2xl mx-auto px-4 py-8">
        <Text
          className="text-white text-4xl mb-4"
          style={{ fontFamily: "Geist-Bold" }}
        >
          Hey, I’m Noufal!
        </Text>
        <Text
          className="text-zinc-400 text-base leading-6"
          style={{ fontFamily: "Geist-Regular" }}
        >
          I’m a <Text className="text-white">Graphic Designer</Text> and a{" "}
          <Text className="text-white">Self-taught Engineer</Text>. I spend my
          time leading design teams, building backend APIs with Python, and
          tinkering with Arch Linux. I prefer logic over dogmas and clean code
          over complex designs.
        </Text>
      </View>
    </View>
  );
}
