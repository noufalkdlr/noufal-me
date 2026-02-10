import { Text, View } from "react-native";
import { useFonts } from 'expo-font';

export default function Page() {

  let [fontsLoaded] = useFonts({
   'Geist-Regular': require('../assets/fonts/Geist-Regular.ttf'),
    'Geist-Bold': require('../assets/fonts/Geist-Bold.ttf'),
    'Geist-Black': require('../assets/fonts/Geist-Black.ttf'),
  })
  if (!fontsLoaded) {
    return null;
  }
  return (
    <View className="flex-1 bg-black ">
      <View className="flex-1 w-full max-w-2xl mx-auto px-4">
        <Text className="text-white text-4xl mb-4" style={{ fontFamily: 'Geist-Black' }}>Hey, I’m Noufal!</Text>
        <Text className="text-white text-base leading-6" style={{ fontFamily: 'Geist-Regular' }}>
          I’m a Graphic Designer and a Self-taught Engineer. I spend my time
          leading design teams, building backend APIs with Python, and tinkering
          with Arch Linux. I prefer logic over dogmas and clean code over
          complex designs.
        </Text>
      </View>
    </View>
  );
}
