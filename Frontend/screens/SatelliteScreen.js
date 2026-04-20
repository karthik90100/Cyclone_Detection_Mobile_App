import { View, Text, TouchableOpacity, Image, ActivityIndicator, ScrollView, StyleSheet } from 'react-native';
import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';

export default function SatelliteScreen() {
    const [image, setImage] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

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
            setResult(null); // reset result
        }
    };

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

            const res = await fetch("http://192.168.0.120:5000/predict-satellite", {
                method: "POST",
                body: formData,
            });

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
            <Text style={styles.title}>
                🛰️ Satellite Detection
            </Text>

            {/* Image Preview */}
            <View style={styles.imageContainer}>
                {image ? (
                    <Image source={{ uri: image }} style={styles.image} />
                ) : (
                    <View style={styles.placeholder}>
                        <Text style={styles.placeholderText}>No Image Selected</Text>
                    </View>
                )}
            </View>

            {/* Upload Button */}
            <TouchableOpacity onPress={pickImage} style={styles.uploadBtn}>
                <Text style={styles.btnText}>Upload Image</Text>
            </TouchableOpacity>

            {/* Detect Button */}
            <TouchableOpacity onPress={detect} style={styles.detectBtn}>
                <Text style={styles.btnText}>Detect Cyclone</Text>
            </TouchableOpacity>

            {/* Loading */}
            {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

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
        backgroundColor: "#f3f4f6",
        padding: 16,
    },
    title: {
        fontSize: 24,
        fontWeight: "bold",
        textAlign: "center",
        color: "#581c87",
    },
    imageContainer: {
        marginTop: 20,
    },
    image: {
        height: 200,
        width: "100%",
        borderRadius: 15,
    },
    placeholder: {
        height: 200,
        backgroundColor: "#d1d5db",
        borderRadius: 15,
        justifyContent: "center",
        alignItems: "center",
    },
    placeholderText: {
        color: "#4b5563",
    },
    uploadBtn: {
        backgroundColor: "#2563eb",
        padding: 15,
        borderRadius: 10,
        marginTop: 20,
    },
    detectBtn: {
        backgroundColor: "#9333ea",
        padding: 15,
        borderRadius: 10,
        marginTop: 10,
    },
    btnText: {
        color: "white",
        textAlign: "center",
        fontWeight: "600",
    },
    resultCard: {
        backgroundColor: "white",
        padding: 15,
        borderRadius: 15,
        marginTop: 20,
    },
    resultTitle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#1f2937",
    },
    resultText: {
        color: "#4b5563",
        marginTop: 5,
    },
});