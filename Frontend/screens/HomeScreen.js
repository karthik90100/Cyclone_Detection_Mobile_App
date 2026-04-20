import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function HomeScreen({ navigation }) {
    return (
        <View style={styles.container}>

            <Text style={styles.title}>
                🌦️ Parjanya Cloud App
            </Text>

            <Text style={styles.subtitle}>
                Detect Cyclones using Ground & Satellite Images
            </Text>

            {/* Go to Ground */}
            <TouchableOpacity
                style={styles.button}
                onPress={() => navigation.navigate("Ground")}
            >
                <Text style={styles.buttonText}>Go to Ground Analysis</Text>
            </TouchableOpacity>

            {/* Go to Satellite */}
            <TouchableOpacity
                style={[styles.button, { backgroundColor: "#9333ea" }]}
                onPress={() => navigation.navigate("Satellite")}
            >
                <Text style={styles.buttonText}>Go to Satellite Detection</Text>
            </TouchableOpacity>

        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#eef2ff",
        padding: 20,
    },
    title: {
        fontSize: 26,
        fontWeight: "bold",
        marginBottom: 10,
        color: "#1e3a8a",
    },
    subtitle: {
        fontSize: 14,
        textAlign: "center",
        marginBottom: 30,
        color: "#4b5563",
    },
    button: {
        backgroundColor: "#2563eb",
        padding: 15,
        borderRadius: 10,
        width: "100%",
        marginTop: 10,
    },
    buttonText: {
        color: "white",
        textAlign: "center",
        fontWeight: "600",
    },
});