import {
    View,
    Text,
    TouchableOpacity,
    Image,
    ActivityIndicator,
    ScrollView,
    StyleSheet
} from 'react-native';

import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';

export default function SatelliteScreen() {

    const [image, setImage] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

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
            setResult(null);
        }
    };

    // 🛰️ Detect Cyclone
    const detect = async () => {
        try {
            if (!image) {
                alert("Upload image first");
                return;
            }

            setLoading(true);

            const formData = new FormData();
            formData.append("file", {
                uri: image,
                name: "photo.jpg",
                type: "image/jpeg",
            });

            const res = await fetch(
                "http://192.168.0.120:5000/satellite",
                {
                    method: "POST",
                    body: formData,
                }
            );

            const data = await res.json();
            setResult(data);

        } catch (error) {
            console.log(error);
            alert("Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={styles.container}>

            {/* Title */}
            <Text style={styles.title}>CycloSense</Text>
            <Text style={styles.subtitle}>
                Satellite Cyclone Detection
            </Text>

            {/* Image Preview */}
            <View style={styles.card}>
                {image ? (
                    <Image source={{ uri: image }} style={styles.image} />
                ) : (
                    <Text style={styles.placeholderText}>
                        🛰️ Select Satellite Image
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

            {/* Detect Button */}
            <TouchableOpacity onPress={detect} disabled={!image}>
                <LinearGradient
                    colors={["#22c55e", "#4ade80"]}
                    style={[
                        styles.gradientBtn,
                        { opacity: image ? 1 : 0.5 }
                    ]}
                >
                    <Text style={styles.btnText}>Detect Cyclone</Text>
                </LinearGradient>
            </TouchableOpacity>

            {/* Loading */}
            {loading && (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#16a34a" />
                    <Text style={styles.loadingText}>
                        Processing satellite data...
                    </Text>
                </View>
            )}

            {/* Result */}
            {result && (
                <View style={styles.resultCard}>
                    <Text style={styles.resultTitle}>
                        Prediction: {result.prediction}
                    </Text>

                    <Text style={styles.resultText}>
                        Confidence: {result.confidence}%
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
        height: 220,
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
        color: "#ffffff",
        fontSize: 16,
        fontWeight: "600",
    },

    loadingContainer: {
        marginTop: 25,
        alignItems: "center",
    },

    loadingText: {
        marginTop: 8,
        color: "#065f46",
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
        fontSize: 16,
        fontWeight: "700",
        color: "#065f46",
    },

    resultText: {
        marginTop: 5,
        color: "#374151",
    },

});