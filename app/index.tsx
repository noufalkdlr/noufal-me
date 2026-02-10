import { Text, View } from "react-native";
import { useFonts, Geist_400Regular, Geist_500Medium, Geist_700Bold, Geist_900Black } from '@expo-google-fonts/geist'

export default function Page() {

  let [fontsLoaded] = useFonts({
    Geist_400Regular,
    Geist_500Medium,
    Geist_700Bold,
    Geist_900Black,
  })
  if (!fontsLoaded) {
    return null;
  }
  return (
    <View className="flex-1 bg-black ">
      <View className="flex-1 w-full max-w-2xl mx-auto px-6 ">
        <Text className="text-white text-4xl mb-4" style={{ fontFamily: 'Geist_700Bold' }}>Hey, I’m Noufal!</Text>
        <Text className="text-white text-base leading-6">
          I’m a Graphic Designer and a Self-taught Engineer. I spend my time
          leading design teams, building backend APIs with Python, and tinkering
          with Arch Linux. I prefer logic over dogmas and clean code over
          complex designs.
        </Text>
      </View>
    </View>
  );
}
