import {
    View,
    Text,
    TouchableOpacity,
    Image,
    ScrollView,
    ActivityIndicator,
    StyleSheet
} from 'react-native';

import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useState, useEffect } from 'react';

import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';

export default function GroundScreen() {

    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigation = useNavigation();
    const [location, setLocation] = useState(null);
    const [locationGranted, setLocationGranted] = useState(false);

    // 📍 Location Permission
    useEffect(() => {
        const requestLocation = async () => {

            let { status } = await Location.getForegroundPermissionsAsync();

            if (status !== "granted") {
                const res = await Location.requestForegroundPermissionsAsync();
                if (res.status !== "granted") {
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

    // 🌱 Detect Cyclone
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

        const formData = new FormData();

        // ✅ FIX: Proper filename + type
        const filename = image.split("/").pop();
        const match = /\.(\w+)$/.exec(filename);
        const fileType = match ? `image/${match[1]}` : `image/jpeg`;

        formData.append("file", {
            uri: image,
            name: filename,
            type: fileType,
        });

        formData.append("lat", location.lat.toString());
        formData.append("lon", location.lon.toString());

        console.log("📤 Sending request...");
        console.log("Image URI:", image);
        console.log("Location:", location);

        const res = await fetch(
            "https://cyclone-detection-mobile-app-1.onrender.com/predict",
            {
                method: "POST",
                body: formData,
            }
        );

        console.log("STATUS:", res.status);

        const text = await res.text();
        console.log("RAW RESPONSE:", text);

        const data = JSON.parse(text);

        // ✅ Handle backend errors properly
        if (!data.success) {
            alert(data.message || "Server failed");
            return;
        }

        if (!data.prediction) {
            alert("Invalid response from server");
            return;
        }

        navigation.navigate("Result", {
            result: data,
            location: location,
        });

    } catch (error) {
    console.log("❌ ERROR OBJECT:", error);
    console.log("❌ ERROR MESSAGE:", error.message);
    console.log("❌ ERROR STRING:", JSON.stringify(error));
    alert(error.message);
}    finally {
        setLoading(false);
    }
};

    // 🚫 If location not granted
    if (!locationGranted) {
        return (
            <View style={styles.center}>
                <Text>📍 Please allow location access</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>

            {/* Title */}
            <Text style={styles.title}>CycloSense</Text>
            <Text style={styles.subtitle}>
                AI Cyclone Detection for Farmers
            </Text>

            {/* Image Card */}
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
            <TouchableOpacity onPress={pickImage}>
                <LinearGradient
                    colors={["#16a34a", "#22c55e"]}
                    style={styles.gradientBtn}
                >
                    <Text style={styles.btnText}>Upload Image</Text>
                </LinearGradient>
            </TouchableOpacity>

            {/* Analyze Button */}
            <TouchableOpacity onPress={detect} disabled={!image}>
                <LinearGradient
                    colors={["#22c55e", "#4ade80"]}
                    style={[
                        styles.gradientBtn,
                        { opacity: image ? 1 : 0.5 }
                    ]}
                >
                    <Text style={styles.btnText}>Analyze</Text>
                </LinearGradient>
            </TouchableOpacity>

            {/* Loading */}
            {loading && (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#16a34a" />
                    <Text style={styles.loadingText}>
                        Analyzing cyclone patterns...
                    </Text>
                </View>
            )}

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

    title: {
        fontSize: 28,
        fontWeight: "700",
        textAlign: "center",
        color: "#065f46",
        marginTop: 40,
    },

    subtitle: {
        textAlign: "center",
        color: "#16a34a",
        marginBottom: 20,
        fontSize: 14,
    },

    card: {
        backgroundColor: "#ffffff",
        borderRadius: 28,
        height: 230,
        justifyContent: "center",
        alignItems: "center",
        marginBottom: 25,
        borderWidth: 1,
        borderColor: "#dcfce7",
        elevation: 6,
    },

    image: {
        width: "100%",
        height: "100%",
        borderRadius: 28,
    },

    placeholderText: {
        color: "#16a34a",
        fontSize: 16,
    },

    gradientBtn: {
        paddingVertical: 16,
        borderRadius: 16,
        marginVertical: 10,
        alignItems: "center",
        elevation: 6,
    },

    btnText: {
        color: "#fff",
        fontWeight: "600",
        fontSize: 16,
    },

    loadingContainer: {
        marginTop: 25,
        alignItems: "center",
    },

    loadingText: {
        marginTop: 8,
        color: "#065f46",
    },
});