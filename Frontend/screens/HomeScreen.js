import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Speech from 'expo-speech';
import { useEffect } from 'react';

export default function HomeScreen({ navigation }) {

    // 🔊 Auto voice when screen loads
    useEffect(() => {
        speakTelugu();

        // Stop voice when leaving screen (important fix)
        return () => {
            Speech.stop();
        };
    }, []);

    // 🎤 Telugu voice function
    const speakTelugu = () => {
        Speech.speak(
            "సైక్లోసెన్స్ కు స్వాగతం. ఇది ఏఐ ఆధారిత తుఫాను గుర్తింపు యాప్.",
            {
                language: "te-IN",
                pitch: 1.0,
                rate: 0.9,
            }
        );
    };

    return (
        <View style={styles.container}>

            {/* Title */}
            <Text style={styles.title}>CycloSense</Text>

            <Text style={styles.subtitle}>
                AI-Powered Cyclone Detection
            </Text>

            {/* Ground Button */}
            <TouchableOpacity onPress={() => navigation.navigate("Ground")}>
                <LinearGradient
                    colors={["#16a34a", "#22c55e"]}
                    style={styles.button}
                >
                    <Text style={styles.buttonText}>
                        🌾 Ground Analysis
                    </Text>
                </LinearGradient>
            </TouchableOpacity>

            {/* Satellite Button */}
            <TouchableOpacity onPress={() => navigation.navigate("Satellite")}>
                <LinearGradient
                    colors={["#22c55e", "#4ade80"]}
                    style={styles.button}
                >
                    <Text style={styles.buttonText}>
                        🛰️ Satellite Detection
                    </Text>
                </LinearGradient>
            </TouchableOpacity>

        </View>
    );
}

const styles = StyleSheet.create({

    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#ecfdf5",
        padding: 20,
    },

    title: {
        fontSize: 32,
        fontWeight: "700",
        color: "#065f46",
        marginBottom: 8,
    },

    subtitle: {
        fontSize: 14,
        textAlign: "center",
        marginBottom: 40,
        color: "#16a34a",
    },

   button: {
    paddingVertical: 16,  
    paddingHorizontal: 25, 
    borderRadius: 16,
    width: "100%", 
    marginTop: 15,
    alignItems: "center",
    elevation: 5,
},

    buttonText: {
        color: "white",
        fontSize: 16,
        fontWeight: "600",
    },

});