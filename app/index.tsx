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
          className="text-zinc-400 text-base leading-6 mb-4"
          style={{ fontFamily: "Geist-Regular" }}
        >
          I’m a <Text className="text-white">Software Engineer</Text> passionate
          about building scalable backend systems with{" "}
          <Text className="text-white">Python & Django</Text>. I love tinkering with{" "}
          <Text className="text-white">Linux</Text> and automating workflows.
        </Text>
        <Text className="text-zinc-400 text-base leading-6">
          With 5 years of experience leading creative teams, I bring a unique
          problem-solving mindset to engineering—focusing on logic, efficiency, and
          clean code.
        </Text>
      </View>
    </View>
  );
}
