export class AudioRecorder {
  private recorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];

  async start(): Promise<void> {
    if (this.recorder) {
      throw new Error("Recorder is already active.");
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("Microphone access is not supported.");
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    const recorder = new MediaRecorder(stream);

    this.chunks = [];
    this.recorder = recorder;

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        this.chunks.push(event.data);
      }
    });

    recorder.addEventListener("stop", () => {
      stream.getTracks().forEach((track) => track.stop());
    });

    recorder.start();
  }

  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.recorder) {
        reject(new Error("Recorder is not active."));
        return;
      }

      const recorder = this.recorder;

      recorder.addEventListener(
        "stop",
        () => {
          const mimeType = recorder.mimeType || "audio/webm";

          const audio = new Blob(this.chunks, {
            type: mimeType,
          });

          this.recorder = null;
          this.chunks = [];

          resolve(audio);
        },
        { once: true },
      );

      recorder.stop();
    });
  }

  isRecording(): boolean {
    return this.recorder?.state === "recording";
  }
}
