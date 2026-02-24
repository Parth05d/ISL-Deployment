import React, { useState, useRef, useEffect } from 'react';
import { User, Circle, History, FileText, BookOpen } from 'lucide-react';
import { predictVideo } from '../services/api';

const Home = () => {
    const videoRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [prediction, setPrediction] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [stream, setStream] = useState(null);
    const [recentLexicon, setRecentLexicon] = useState([
        // { word: 'Greetings', time: '14:02' },
        // { word: 'Gratitude', time: '13:58' },
        // { word: 'Inquiry', time: '13:45' },
    ]);

    useEffect(() => {
        startCamera();
        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Could not access camera. Please allow camera permissions.");
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    };

    const startRecording = () => {
        if (!stream) return;

        setPrediction(null);
        setIsRecording(true);
        setRecordingTime(0);

        const chunks = [];
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            setIsRecording(false);
            setIsProcessing(true);
            const blob = new Blob(chunks, { type: 'video/webm' });

            try {
                const result = await predictVideo(blob);
                setPrediction(result);
                // Add to recent history
                if (result.prediction) {
                    setRecentLexicon(prev => [{ word: result.prediction, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }, ...prev].slice(0, 5));
                }
            } catch (err) {
                console.error(err);
                alert("Prediction failed. See console for details.");
            } finally {
                setIsProcessing(false);
            }
        };

        mediaRecorder.start();

        // Timer Logic
        let timeLeft = 0;
        const interval = setInterval(() => {
            timeLeft += 100; // 100ms
            setRecordingTime(prev => prev + 100);
            if (timeLeft >= 2000) {
                clearInterval(interval);
                mediaRecorder.stop();
            }
        }, 100);
    };

    return (
        <div className="w-full space-y-16">
            <div className="w-full text-center space-y-6 max-w-3xl mx-auto">
                <h2 className="text-5xl md:text-6xl font-serif text-charcoal italic leading-tight pt-8">
                    Refined <span className="text-crimson not-italic font-bold">Linguistic Bridge</span> for the Deaf
                </h2>
                <p className="text-lg text-slate-600 max-w-xl mx-auto leading-relaxed font-light">
                    An advanced optical recognition engine translating Indian Sign Language into academic-grade text with unparalleled precision.
                </p>
            </div>

            <div className="w-full grid lg:grid-cols-12 gap-12 items-start">
                {/* Camera Section */}
                <div className="lg:col-span-8 flex flex-col gap-8">
                    <div className="relative w-full aspect-video crimson-border bg-white overflow-hidden group rounded-lg shadow-xl">
                        {/* Video Feed */}
                        <video
                            ref={videoRef}
                            autoPlay
                            muted
                            playsInline
                            className="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                        />

                        {/* Overlay when not recording/ready */}
                        {!stream && (
                            <div className="absolute inset-0 bg-[#F2F0E9] flex flex-col items-center justify-center z-10">
                                <User className="w-16 h-16 text-crimson mb-4 opacity-40" />
                                <p className="text-charcoal font-serif italic text-lg opacity-60">Awaiting Signal Input...</p>
                            </div>
                        )}

                        <div className="absolute top-6 left-6 flex items-center gap-3 z-20">
                            <div className="flex items-center gap-2 px-3 py-1.5 glass-panel text-crimson text-[10px] font-bold uppercase tracking-widest border border-white/50 rounded-full">
                                <span className={`w-1.5 h-1.5 bg-crimson rounded-full ${isRecording ? 'animate-pulse' : ''}`}></span>
                                {isRecording ? 'Recording...' : 'Live Optical Feed'}
                            </div>
                        </div>

                        {/* Processing Overlay */}
                        {isProcessing && (
                            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-30 flex flex-col items-center justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-crimson mb-4"></div>
                                <p className="text-crimson font-serif font-bold text-lg">Synthesizing Prediction...</p>
                            </div>
                        )}
                    </div>

                    {/* Controls */}
                    <div className="flex justify-center relative w-full">
                        <button
                            onClick={startRecording}
                            disabled={isRecording || isProcessing}
                            className={`
                                group relative overflow-hidden flex items-center justify-center gap-4 
                                bg-white text-crimson w-72 h-14 text-sm font-bold uppercase tracking-[0.2em] 
                                shadow-lg transition-all duration-300 border border-crimson
                                ${isRecording ? 'pointer-events-none' : 'hover:bg-crimson hover:text-white'}
                            `}
                        >
                            {isRecording ? (
                                <div className="absolute inset-0 w-full h-full bg-white flex flex-col justify-center px-6">
                                    <div className="flex justify-between items-center text-[10px] text-crimson font-bold tracking-widest w-full mb-2">
                                        <span>Recording</span>
                                        <Circle className="w-2 h-2 fill-crimson animate-pulse" />
                                    </div>
                                    <div className="h-1 w-full bg-stone-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-crimson transition-all duration-100 ease-linear"
                                            style={{ width: `${(recordingTime / 2000) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <Circle className="w-4 h-4 fill-current group-hover:scale-110 transition-transform" />
                                    <span>Initiate Capture</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Sidebar / Output */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="glass-panel p-8 border border-crimson/10 flex flex-col gap-8 h-full min-h-[480px]">
                        <div className="space-y-4">
                            <span className="text-[10px] font-bold uppercase text-crimson tracking-[0.2em]">Translation Output</span>
                            <div className="h-40 flex items-center justify-center border-b border-stone-200 bg-white/50 rounded-sm">
                                {prediction ? (
                                    <div className="text-center">
                                        <p className="text-4xl font-serif italic text-charcoal mb-2">"{prediction.prediction}"</p>
                                        <span className="text-xs text-stone-400 font-mono">Confidence: {(prediction.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                ) : (
                                    <p className="text-stone-400 italic">Waiting for input...</p>
                                )}
                            </div>
                        </div>

                        <div className="flex-grow flex flex-col gap-4">
                            <div className="flex items-center justify-between">
                                <h3 className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Recent Lexicon</h3>
                                <History className="w-4 h-4 text-stone-300" />
                            </div>
                            <div className="space-y-2 scroll-minimal overflow-y-auto max-h-64 pr-2">
                                {recentLexicon.map((item, idx) => (
                                    <div key={idx} className="flex items-baseline justify-between py-3 border-b border-stone-100 last:border-0">
                                        <span className="text-sm text-charcoal font-medium">{item.word}</span>
                                        <span className="text-[10px] text-stone-400 font-serif">{item.time}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* <button className="w-full py-3 border border-stone-200 text-[10px] font-bold uppercase tracking-widest hover:border-crimson hover:text-crimson transition-all flex items-center justify-center gap-2">
                            <FileText className="w-4 h-4" />
                            Export Transcript
                        </button> */}
                    </div>
                </div>
            </div>

            {/* Features Footer */}
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-12 pt-8 border-t border-stone-200">
                <div className="space-y-4">
                    <BookOpen className="text-crimson w-8 h-8" />
                    <h3 className="text-lg font-serif font-bold text-charcoal">Linguistic Precision</h3>
                    <p className="text-sm text-stone-500 leading-relaxed">Our models are trained on classical ISL corpora to ensure formal and accurate syntax translation.</p>
                </div>
                <div className="space-y-4">
                    <User className="text-crimson w-8 h-8" />
                    <h3 className="text-lg font-serif font-bold text-charcoal">Neural Synthesis</h3>
                    <p className="text-sm text-stone-500 leading-relaxed">Real-time gesture analysis using state-of-the-art computer vision architectures.</p>
                </div>
                <div className="space-y-4">
                    <History className="text-crimson w-8 h-8" />
                    <h3 className="text-lg font-serif font-bold text-charcoal">Inclusive Pedagogy</h3>
                    <p className="text-sm text-stone-500 leading-relaxed">Designed in collaboration with linguists and the Deaf community for academic excellence.</p>
                </div>
            </div>
        </div>
    );
};

export default Home;
