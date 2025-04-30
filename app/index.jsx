import React, { useState } from 'react';
import { View, Button, StyleSheet, Text } from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';
import Player from '../assets/components/Player'; // Adjust if needed

export default function App() {
  const [recording, setRecording] = useState(null);
  const [originalUri, setOriginalUri] = useState(null);
  const [processedUri, setProcessedUri] = useState(null);

  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    setRecording(undefined);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    setOriginalUri(uri);
    await sendToBackend(uri);
  };

  const sendToBackend = async (uri) => {
    const formData = new FormData();
    formData.append('file', {
      uri,
      name: 'audio.wav',
      type: 'audio/wav',
    });

    try {
      const response = await axios({
        method: 'POST',
        url: 'http://192.168.1.72:8080/',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'arraybuffer', // correct for binary data!
      });

      const processedPath = FileSystem.cacheDirectory + 'processed.wav';
      await FileSystem.writeAsStringAsync(
        processedPath,
        Buffer.from(response.data).toString('base64'),
        { encoding: FileSystem.EncodingType.Base64 }
      );
      setProcessedUri(processedPath);
    } catch (error) {
      console.error('Upload failed', error);
    }
  };

  return (
    <View style={styles.container}>
      <Button
        title={recording ? 'Stop Recording' : 'Start Recording'}
        onPress={recording ? stopRecording : startRecording}
      />
      {originalUri && (
        <>
          <Text>Original Audio:</Text>
          <Player uri={originalUri} />
        </>
      )}
      {processedUri && (
        <>
          <Text>Processed Audio:</Text>
          <Player uri={processedUri} />
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
});
