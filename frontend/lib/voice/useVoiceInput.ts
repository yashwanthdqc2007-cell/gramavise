"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { VoiceFieldType, VoiceListeningState, ParseResult } from "./types";
import { parseVoiceNumber } from "./numericParser";
import { useTranslation } from "@/lib/i18n";

// Map Step 5A language code to BCP 47 Speech Recognition locale
const SPEECH_LOCALE_MAP: Record<string, string> = {
  en: "en-IN",
  hi: "hi-IN",
  mr: "mr-IN",
  bn: "bn-IN",
  te: "te-IN",
  ta: "ta-IN",
};

export function useVoiceInput(onValueConfirmed: (fieldType: VoiceFieldType, value: number) => void) {
  const { language } = useTranslation();
  const [state, setState] = useState<VoiceListeningState>("IDLE");
  const [activeField, setActiveField] = useState<VoiceFieldType | null>(null);
  const [rawTranscript, setRawTranscript] = useState<string>("");
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const isMountedRef = useRef<boolean>(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const isSupported = typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const startListening = useCallback(
    (fieldType: VoiceFieldType) => {
      if (!isSupported) {
        setState("UNSUPPORTED");
        setActiveField(fieldType);
        setErrorMessage("Voice recognition is not supported on this browser.");
        return;
      }

      // Reset prior state
      setRawTranscript("");
      setParseResult(null);
      setErrorMessage(null);
      setActiveField(fieldType);
      setState("REQUESTING_PERMISSION");

      try {
        const SpeechRecognitionClass =
          (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognitionClass();
        recognitionRef.current = recognition;

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.lang = SPEECH_LOCALE_MAP[language] || "en-IN";

        recognition.onstart = () => {
          if (isMountedRef.current) {
            setState("LISTENING");
          }
        };

        recognition.onresult = (event: any) => {
          if (!isMountedRef.current) return;
          const transcript = event.results?.[0]?.[0]?.transcript || "";
          setRawTranscript(transcript);
          setState("PARSING");

          // Run deterministic parser
          const result = parseVoiceNumber(transcript, fieldType);
          setParseResult(result);
          setState("AWAITING_CONFIRMATION");
        };

        recognition.onerror = (event: any) => {
          if (!isMountedRef.current) return;
          const err = event.error;
          if (err === "not-allowed" || err === "service-not-allowed") {
            setState("PERMISSION_DENIED");
            setErrorMessage("Microphone permission was denied. Please allow microphone access or type manually.");
          } else if (err === "network") {
            setState("RECOGNITION_ERROR");
            setErrorMessage("Voice recognition is unavailable offline. You can easily enter the value using the keyboard.");
          } else if (err === "no-speech") {
            setState("NO_SPEECH");
            setErrorMessage("No speech was detected. Please try again or type manually.");
          } else {
            setState("RECOGNITION_ERROR");
            setErrorMessage(`Recognition error: ${err}. Please try again or type manually.`);
          }
        };

        recognition.onend = () => {
          if (!isMountedRef.current) return;
          // If onend fires while in LISTENING state without results, trigger NO_SPEECH
          setState((prev) => (prev === "LISTENING" || prev === "REQUESTING_PERMISSION" ? "NO_SPEECH" : prev));
        };

        recognition.start();
      } catch (err: any) {
        if (isMountedRef.current) {
          setState("RECOGNITION_ERROR");
          setErrorMessage("Failed to start speech recognition.");
        }
      }
    },
    [isSupported, language]
  );

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
    }
  }, []);

  const confirmValue = useCallback(() => {
    if (activeField && parseResult && parseResult.status === "SUCCESS" && parseResult.parsed_value !== null) {
      // Execute the callback to update form state
      onValueConfirmed(activeField, parseResult.parsed_value);
      // Reset state to IDLE
      setState("IDLE");
      setActiveField(null);
      setParseResult(null);
      setRawTranscript("");
    }
  }, [activeField, parseResult, onValueConfirmed]);

  const retry = useCallback(() => {
    if (activeField) {
      startListening(activeField);
    }
  }, [activeField, startListening]);

  const cancel = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // ignore
      }
    }
    setState("IDLE");
    setActiveField(null);
    setParseResult(null);
    setRawTranscript("");
    setErrorMessage(null);
  }, []);

  return {
    isSupported,
    state,
    activeField,
    rawTranscript,
    parseResult,
    errorMessage,
    startListening,
    stopListening,
    confirmValue,
    retry,
    cancel,
  };
}
