import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import MapView, { Marker } from "react-native-maps";
import * as Speech from "expo-speech";

export default function ResultScreen({ route }) {

    const { result, location } = route.params || {};
    const [language, setLanguage] = useState("te"); // default Telugu

    // 🛑 No data
    if (!result || !location) {
        return (
            <View style={styles.center}>
                <Text>No data received</Text>
            </View>
        );
    }

    // 🛑 Backend error
    if (!result.success) {
        return (
            <View style={styles.center}>
                <Text>{result.message || "Something went wrong"}</Text>
            </View>
        );
    }

    // ✅ Data
    const cyclone = result.prediction || "Unknown";
    const weather = result.weather || {};

    const rainChance = result.rainChance || "Unknown";
    const riskLevel = result.riskLevel || "Unknown";

    const weatherCondition = weather.condition || "Unknown";
    const wind = weather.windSpeed ?? "N/A";
    const humidity = weather.humidity ?? "N/A";
    const pressure = weather.pressure ?? "N/A";
    const confidence = result.confidence ?? "N/A";

    const windText = wind !== "N/A" ? wind : "not available";

    // 🎯 Risk color
    const getRiskColor = (risk) => {
        if (!risk) return "#16a34a";
        const r = risk.toLowerCase();
        if (r === "high") return "#dc2626";
        if (r === "medium") return "#ca8a04";
        return "#16a34a";
    };

    // 🔊 Telugu Auto Voice
    const speakTelugu = () => {
    Speech.stop(); // reset

    const text = `తుఫాను ప్రమాద స్థాయి ${riskLevel}. 
    వర్షం వచ్చే అవకాశం ${rainChance}. 
    వాతావరణం ${weatherCondition}. 
    గాలి వేగం గంటకు ${windText} కిలోమీటర్లు.`;

    Speech.speak(text, {
        language: "te-IN",
        rate: 0.9,
        pitch: 1,
    });
};

    // 🔊 English Voice (Button)
    const speakEnglish = () => {
        Speech.stop();

        const text = `Cyclone risk is ${riskLevel}. 
        Rain chance is ${rainChance}. 
        Weather is ${weatherCondition}. 
        Wind speed is ${windText} kilometers per hour.`;

        Speech.speak(text, {
            language: "en-US",
            rate: 0.9,
        });
    };

    // 🚀 AUTO VOICE ON LOAD (TELUGU)
useEffect(() => {
    if (result && location) {
        const timer = setTimeout(() => {
            speakTelugu();
        }, 500);

        return () => {
            clearTimeout(timer); // clear timer
            Speech.stop();       // 🛑 stop voice when leaving screen
        };
    }
}, [result, location]);

    return (
        <ScrollView
            style={styles.container}
            contentContainerStyle={{ paddingBottom: 40 }}
        >

            {/* HEADER */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Cyclone Monitor</Text>
                <Text style={styles.headerSub}>Smart Farming Protection</Text>
            </View>

            {/* MAP */}
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
                    <Marker coordinate={{ latitude: location.lat, longitude: location.lon }} />
                </MapView>

                <View style={styles.overlayCard}>
                    <Text style={styles.overlayText}>Your Location</Text>
                </View>
            </View>

            {/* 🌪️ RISK */}
            <View style={styles.statusCard}>
                <Text style={styles.statusTitle}>Cyclone Risk</Text>
                <Text style={[styles.statusValue, { color: getRiskColor(riskLevel) }]}>
                    {riskLevel}
                </Text>
            </View>

            {/* 📊 GRID */}
            <View style={styles.grid}>

                <View style={styles.card}>
                    <Text style={styles.label}>🌧 Rain Chance</Text>
                    <Text style={styles.value}>{rainChance}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>☁️ Cloud Type</Text>
                    <Text style={styles.value}>{cyclone}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>🌦 Weather</Text>
                    <Text style={styles.value}>{weatherCondition}</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>💨 Wind</Text>
                    <Text style={styles.value}>
                        {wind !== "N/A" ? `${wind} km/h` : "N/A"}
                    </Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>💧 Humidity</Text>
                    <Text style={styles.value}>
                        {humidity !== "N/A" ? `${humidity}%` : "N/A"}
                    </Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>🌡 Pressure</Text>
                    <Text style={styles.value}>
                        {pressure !== "N/A" ? `${pressure} hPa` : "N/A"}
                    </Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.label}>📊 Confidence</Text>
                    <Text style={styles.value}>
                        {confidence !== "N/A" ? `${confidence}%` : "N/A"}
                    </Text>
                </View>

            </View>

            {/* 🔊 BUTTON (ENGLISH ONLY) */}
            <TouchableOpacity style={styles.button} onPress={speakEnglish}>
                <Text style={styles.buttonText}>🔊 Voice Alert (English)</Text>
            </TouchableOpacity>

        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#ecfdf5",
        padding: 16,
    },
    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
    },
    header: { marginBottom: 15 },
    headerTitle: {
        fontSize: 24,
        fontWeight: "bold",
        color: "#065f46",
    },
    headerSub: { color: "#047857" },

    mapWrapper: {
        height: 200,
        borderRadius: 20,
        overflow: "hidden",
        marginBottom: 15,
    },
    map: { width: "100%", height: "100%" },

    overlayCard: {
        position: "absolute",
        bottom: 10,
        left: 10,
        backgroundColor: "#ffffffcc",
        padding: 6,
        borderRadius: 10,
    },
    overlayText: { fontSize: 12, color: "#065f46" },

    statusCard: {
        backgroundColor: "#d1fae5",
        padding: 18,
        borderRadius: 16,
        alignItems: "center",
        marginBottom: 15,
    },
    statusTitle: { color: "#047857" },
    statusValue: {
        fontSize: 26,
        fontWeight: "bold",
        marginTop: 5,
    },

    grid: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
    },

    card: {
        width: "48%",
        backgroundColor: "#ffffff",
        padding: 14,
        borderRadius: 14,
        marginBottom: 10,
        elevation: 2,
    },

    label: { color: "#065f46", fontSize: 12 },
    value: {
        fontSize: 16,
        fontWeight: "bold",
        marginTop: 5,
    },

    button: {
        backgroundColor: "#16a34a",
        padding: 15,
        borderRadius: 14,
        marginTop: 20,
    },

    buttonText: {
        color: "#fff",
        textAlign: "center",
        fontWeight: "bold",
    },
});