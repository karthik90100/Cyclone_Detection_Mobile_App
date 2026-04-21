import {
    View,
    Text,
    TouchableOpacity,
    Image,
    ScrollView,
    ActivityIndicator,
    StyleSheet
} from 'react-native';
import { useNavigation } from '@react-navigation/native';

import { useState, useEffect } from 'react';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import * as Speech from 'expo-speech';

export default function GroundScreen() {

    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigation = useNavigation();
    const [location, setLocation] = useState(null);
    const [locationGranted, setLocationGranted] = useState(false);

    // 📍 Ask Location Permission BEFORE screen loads
    useEffect(() => {
        const requestLocation = async () => {

            const { status } = await Location.getForegroundPermissionsAsync();

            if (status !== "granted") {
                const { status: newStatus } = await Location.requestForegroundPermissionsAsync();

                if (newStatus !== "granted") {
                    alert("📍 Location permission is required");
                    return;
                }
            }

            const loc = await Location.getCurrentPositionAsync({});

            setLocation({
                lat: loc.coords.latitude,
                lon: loc.coords.longitude,
            });

            setLocationGranted(true);
        };

        requestLocation();
    }, []);
    // 📷 Pick Image
    const pickImage = async () => {
        const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();

        if (!permission.granted) {
            alert("Permission required!");
            return;
        }

        const res = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
        });

        if (!res.canceled) {
            setImage(res.assets[0].uri);
        }
    };

    // 🌱 Analyze Function
    const detect = async () => {
        try {
            if (!image) {
                alert("Please upload image first");
                return;
            }

            if (!location) {
                alert("Location not available");
                return;
            }

            setLoading(true);

            const imageUri = image.startsWith("file://") ? image : `file://${image}`;

            const formData = new FormData();

            formData.append("file", {
                uri: imageUri,
                name: "photo.jpg",
                type: "image/jpeg",
            });

            formData.append("lat", location.lat.toString());
            formData.append("lon", location.lon.toString());

            const res = await fetch(
                "https://cyclone-detection-mobile-app.onrender.com/predict",
                {
                    method: "POST",
                    body: formData,
                }
            );

            // 🔥 HANDLE SERVER ERROR
            if (!res.ok) {
                const text = await res.text();
                console.log("SERVER ERROR:", text);
                alert("Server error");
                return;
            }

            const data = await res.json();

            console.log("API RESPONSE:", data);

            // 🔥 IMPORTANT SAFETY CHECK
            if (!data || !data.prediction) {
                alert("Invalid response from server");
                return;
            }

            // 🔥 HANDLE INVALID IMAGE CASE
            if (data.prediction === "Invalid Image") {
                alert("Please upload a valid cloud image");
                return;
            }
            if (!data.weather) {
                data.weather = {};
            }

            navigation.navigate("Result", {
                result: data,
                location: location,
            });

        } catch (error) {
            console.log("ERROR:", error);
            alert("Something went wrong");
        } finally {
            setLoading(false);
        }
    };
    // 🚫 If location not allowed
    if (!locationGranted) {
        return (
            <View style={styles.center}>
                <Text style={{ fontSize: 16 }}>
                    📍 Please allow location access
                </Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>

            <Text style={styles.title}>🌾 Ground Analysis</Text>

            {/* Image Preview Card */}
            <View style={styles.card}>
                {image ? (
                    <Image source={{ uri: image }} style={styles.image} />
                ) : (
                    <Text style={styles.placeholderText}>
                        📷 Select Image
                    </Text>
                )}
            </View>

            {/* Upload Button */}
            <TouchableOpacity onPress={pickImage} style={styles.uploadBtn}>
                <Text style={styles.btnText}>📷 Upload Image</Text>
            </TouchableOpacity>

            {/* Analyze Button */}
            <TouchableOpacity
                onPress={detect}
                style={[styles.analyzeBtn, { opacity: image ? 1 : 0.5 }]}
                disabled={!image}
            >
                <Text style={styles.btnText}>🌱 Analyze</Text>
            </TouchableOpacity>

            {/* Loading */}
            {loading && (
                <View style={{ marginTop: 20 }}>
                    <ActivityIndicator size="large" />
                    <Text style={{ textAlign: "center" }}>
                        Analyzing...
                    </Text>
                </View>
            )}

        </ScrollView>
    );
}

// 🎨 STYLES (GREEN FARMER UI)
const styles = StyleSheet.create({

    container: {
        flex: 1,
        backgroundColor: "#f0fdf4",
        padding: 16,
    },

    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
    },

    title: {
        fontSize: 26,
        fontWeight: "700",
        textAlign: "center",
        color: "#14532d",
        marginTop: 40,
        marginBottom: 15,
    },

    card: {
        backgroundColor: "#ffffff",
        borderRadius: 20,
        height: 200,
        justifyContent: "center",
        alignItems: "center",
        marginBottom: 20,
        elevation: 5,
    },

    image: {
        width: "100%",
        height: "100%",
        borderRadius: 20,
    },

    placeholderText: {
        color: "#166534",
        fontSize: 16,
    },

    uploadBtn: {
        backgroundColor: "#16a34a",
        padding: 14,
        borderRadius: 12,
        marginVertical: 6,
    },

    analyzeBtn: {
        backgroundColor: "#22c55e",
        padding: 14,
        borderRadius: 12,
        marginVertical: 6,
    },

    btnText: {
        color: "white",
        textAlign: "center",
        fontWeight: "600",
        fontSize: 16,
    },

    resultCard: {
        backgroundColor: "#ffffff",
        padding: 16,
        borderRadius: 16,
        marginTop: 20,
        borderLeftWidth: 5,
        borderLeftColor: "#16a34a",
    },

    resultTitle: {
        fontSize: 18,
        fontWeight: "700",
        color: "#14532d",
    },

    resultText: {
        color: "#374151",
        marginTop: 5,
    },

    riskText: {
        color: "#dc2626",
        fontWeight: "bold",
        marginTop: 8,
    },

    voiceBtn: {
        backgroundColor: "#f59e0b",
        padding: 12,
        borderRadius: 10,
        marginTop: 10,
    },
});