import React, { useEffect, useMemo, useRef, useState } from 'react';

const SpeechPlaybackControls = ({ text, language = 'english' }) => {
  const [supported, setSupported] = useState(false);
  const [status, setStatus] = useState('idle');
  const utteranceQueueRef = useRef([]);
  const chunkIndexRef = useRef(0);

  const locale = useMemo(() => {
    const localeMap = {
      english: 'en-IN',
      hindi: 'hi-IN',
      marathi: 'mr-IN',
      tamil: 'ta-IN',
      bengali: 'bn-IN'
    };

    return localeMap[language] || 'en-IN';
  }, [language]);

  const normalizedText = useMemo(() => String(text || '').replace(/\s+/g, ' ').trim(), [text]);

  const stopPlayback = () => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      return;
    }

    utteranceQueueRef.current = [];
    chunkIndexRef.current = 0;
    window.speechSynthesis.cancel();
    setStatus('idle');
  };

  const speakNextChunk = () => {
    const synth = window.speechSynthesis;
    const chunks = utteranceQueueRef.current;
    const chunk = chunks[chunkIndexRef.current];

    if (!chunk) {
      setStatus('idle');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(chunk);
    utterance.lang = locale;
    utterance.rate = 1;
    utterance.onend = () => {
      chunkIndexRef.current += 1;
      if (chunkIndexRef.current < chunks.length) {
        speakNextChunk();
      } else {
        setStatus('idle');
      }
    };
    utterance.onerror = () => {
      setStatus('idle');
    };
    synth.speak(utterance);
  };

  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setSupported(false);
      return undefined;
    }

    setSupported(true);
    return () => {
      stopPlayback();
    };
  }, []);

  if (!normalizedText || !supported) {
    return null;
  }

  const handlePlay = () => {
    const synth = window.speechSynthesis;
    if (status === 'paused') {
      synth.resume();
      setStatus('playing');
      return;
    }

    stopPlayback();
    utteranceQueueRef.current = normalizedText.match(/.{1,220}(\s|$)/g) || [normalizedText];
    chunkIndexRef.current = 0;
    setStatus('playing');
    speakNextChunk();
  };

  const handlePause = () => {
    window.speechSynthesis.pause();
    setStatus('paused');
  };

  const handleStop = () => {
    stopPlayback();
  };

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2 pt-3 border-t border-gray-200">
      <button
        type="button"
        onClick={handlePlay}
        className="inline-flex items-center rounded-md bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700"
      >
        {status === 'paused' ? 'Resume' : 'Play'}
      </button>
      <button
        type="button"
        onClick={handlePause}
        disabled={status !== 'playing'}
        className="inline-flex items-center rounded-md bg-amber-100 px-3 py-1.5 text-xs font-medium text-amber-800 disabled:opacity-50"
      >
        Pause
      </button>
      <button
        type="button"
        onClick={handleStop}
        disabled={status === 'idle'}
        className="inline-flex items-center rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-800 disabled:opacity-50"
      >
        Stop
      </button>
    </div>
  );
};

export default SpeechPlaybackControls;
