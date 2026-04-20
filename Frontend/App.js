import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';

import GroundScreen from './screens/GroundScreen';
import ResultScreen from './screens/ResultScreen';
import SatelliteScreen from './screens/SatelliteScreen';
import HomeScreen from './screens/HomeScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 🔥 Ground Stack (IMPORTANT)
function GroundStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="GroundMain"
        component={GroundScreen}
        options={{ title: "Ground Analysis" }}
      />
      <Stack.Screen
        name="Result"
        component={ResultScreen}
        options={{ title: "Analysis Report" }}
      />
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator screenOptions={{ headerShown: false }}>

        <Tab.Screen name="Home" component={HomeScreen} />

        {/* 👇 Replace GroundScreen with GroundStack */}
        <Tab.Screen name="Ground" component={GroundStack} />

        <Tab.Screen name="Satellite" component={SatelliteScreen} />

      </Tab.Navigator>
    </NavigationContainer>
  );
}