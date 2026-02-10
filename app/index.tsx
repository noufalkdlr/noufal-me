import { Text, View } from "react-native";

export default function Page() {
  return (
    <View className="flex-1 bg-black">
      <View className="flex-1 w-full max-w-2xl mx-auto bg-white">
        <Text>Hey, I’m Noufal!</Text>
        <Text>
          I’m a Graphic Designer and a Self-taught Engineer. I spend my time
          leading design teams, building backend APIs with Python, and tinkering
          with Arch Linux. I prefer logic over dogmas and clean code over
          complex designs.
        </Text>
      </View>
    </View>
  );
}
