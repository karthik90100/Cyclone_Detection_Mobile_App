import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import MapView, { Marker } from "react-native-maps";
import * as Speech from 'expo-speech';

export default function ResultScreen({ route }) {

    const { result, location } = route.params || {};

    if (!result || !location) {
        return (
            <View style={styles.center}>
                <Text>No data received</Text>
            </View>
        );
    }

    const cyclone = result.risk || "Unknown";
    const rain = result.weather?.condition || "Moderate";

    const getRiskColor = (risk) => {
        if (risk?.toLowerCase().includes("cyclone")) return "#dc2626";
        if (risk?.toLowerCase().includes("storm")) return "#ca8a04";
        return "#16a34a";
    };

    const speak = () => {
        Speech.speak(`Cyclone risk is ${cyclone}. Rainfall is ${rain}`);
    };

    return (
        <ScrollView style={styles.container}>

            {/* 🌿 HEADER */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>🌿 Cyclone Monitor</Text>
                <Text style={styles.headerSub}>Smart Farming Protection</Text>
            </View>

            {/* 🗺️ MAP (FIXED) */}
            <View style={styles.mapWrapper}>
                <MapView
                    style={styles.map}
                    initialRegion={{
                        latitude: location.lat,
                        longitude: location.lon,
                        latitudeDelta: 0.01,
                        longitudeDelta: 0.01,
                    }}
                >
                    <Marker
                        coordinate={{
                            latitude: location.lat,
                            longitude: location.lon,
                        }}
                    />
                </MapView>

                {/* Overlay Card */}
                <View style={styles.overlayCard}>
                    <Text style={styles.overlayText}>📍 Your Farm Location</Text>
                </View>
            </View>

            {/* 🌪️ MAIN STATUS */}
            <View style={styles.statusCard}>
                <Text style={styles.statusTitle}>Cyclone Status</Text>
                <Text style={[styles.statusValue, { color: getRiskColor(cyclone) }]}>
                    {cyclone}
                </Text>
            </View>

            {/* 📊 GRID */}
            <View style={styles.grid}>

                <View style={styles.card}>
                    <Text style={styles.label}>🌧 Rain</Text>
                    <Text style={styles.value}>{rain}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>🤖 Prediction</Text>
                    <Text style={styles.value}>{result.prediction}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>💨 Wind</Text>
                    <Text style={styles.value}>{result.weather?.windSpeed}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>💧 Humidity</Text>
                    <Text style={styles.value}>{result.weather?.humidity}%</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>🌡 Pressure</Text>
                    <Text style={styles.value}>{result.weather?.pressure}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>📊 Confidence</Text>
                    <Text style={styles.value}>{result.confidence}%</Text>
                </View>

            </View>

            {/* 🔊 BUTTON */}
            <TouchableOpacity style={styles.button} onPress={speak}>
                <Text style={styles.buttonText}>🔊 Voice Alert</Text>
            </TouchableOpacity>

        </ScrollView>
    );
}

const styles = StyleSheet.create({

    container: {
        flex: 1,
        backgroundColor: "#ecfdf5",
        padding: 16
    },

    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center"
    },

    header: {
        marginBottom: 15
    },

    headerTitle: {
        fontSize: 24,
        fontWeight: "bold",
        color: "#065f46"
    },

    headerSub: {
        color: "#047857"
    },

    mapWrapper: {
        height: 200,
        borderRadius: 20,
        overflow: "hidden",
        marginBottom: 15
    },

    map: {
        width: "100%",
        height: "100%"
    },

    overlayCard: {
        position: "absolute",
        bottom: 10,
        left: 10,
        backgroundColor: "#ffffffcc",
        padding: 6,
        borderRadius: 10
    },

    overlayText: {
        fontSize: 12,
        color: "#065f46"
    },

    statusCard: {
        backgroundColor: "#d1fae5",
        padding: 18,
        borderRadius: 16,
        alignItems: "center",
        marginBottom: 15
    },

    statusTitle: {
        color: "#047857"
    },

    statusValue: {
        fontSize: 26,
        fontWeight: "bold",
        marginTop: 5
    },

    grid: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between"
    },

    card: {
        width: "48%",
        backgroundColor: "#ffffff",
        padding: 14,
        borderRadius: 14,
        marginBottom: 10,
        elevation: 2
    },

    label: {
        color: "#065f46",
        fontSize: 12
    },

    value: {
        fontSize: 16,
        fontWeight: "bold",
        marginTop: 5
    },

    button: {
        backgroundColor: "#16a34a",
        padding: 15,
        borderRadius: 14,
        marginTop: 15
    },

    buttonText: {
        color: "#fff",
        textAlign: "center",
        fontWeight: "bold"
    }

});