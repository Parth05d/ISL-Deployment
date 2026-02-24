import React, { useState } from 'react';
import {
  Ship,
  Sun,
  Search,
  ThumbsDown,
  Hand,
  Camera,
  Car,
  CheckCircle,
  Users,
  Moon,
  Utensils,
  ThumbsUp,
  Home,
  User,
  Heart,
  Handshake
} from "lucide-react";

const DICTIONARY_DATA = [
  {
    id: "#0001",
    word: "Aboard",
    category: "Travel",
    type: "Action",
    desc: "Both hands indicate entering or getting onto a vehicle.",
    icon: Ship,
    tag: "Common",
  },
  {
    id: "#0002",
    word: "Afternoon",
    category: "Time",
    type: "Daily",
    desc: "Dominant hand moves downward showing the sun passing noon.",
    icon: Sun,
    tag: null,
  },
  {
    id: "#0003",
    word: "Bad",
    category: "Expression",
    type: "Emotion",
    desc: "Hand moves downward from mouth with negative expression.",
    icon: ThumbsDown,
    tag: null,
  },
  {
    id: "#0004",
    word: "Bye",
    category: "Greeting",
    type: "Common",
    desc: "Open hand waves side to side.",
    icon: Hand,
    tag: "Common",
  },
  {
    id: "#0005",
    word: "Camera",
    category: "Object",
    type: "Device",
    desc: "Hands form a rectangle like holding a camera.",
    icon: Camera,
    tag: null,
  },
  {
    id: "#0006",
    word: "Car",
    category: "Transport",
    type: "Vehicle",
    desc: "Hands hold imaginary steering wheel.",
    icon: Car,
    tag: null,
  },
  {
    id: "#0007",
    word: "Correct",
    category: "Expression",
    type: "Response",
    desc: "Index finger moves forward with confident nod.",
    icon: CheckCircle,
    tag: null,
  },
  {
    id: "#0008",
    word: "Daughter",
    category: "Family",
    type: "Relation",
    desc: "Girl sign followed by child sign.",
    icon: Users,
    tag: null,
  },
  {
    id: "#0009",
    word: "Evening",
    category: "Time",
    type: "Daily",
    desc: "Hand moves downward representing sunset.",
    icon: Moon,
    tag: null,
  },
  {
    id: "#0010",
    word: "Food",
    category: "Daily Life",
    type: "Noun",
    desc: "Fingers touch mouth repeatedly.",
    icon: Utensils,
    tag: "Common",
  },
  {
    id: "#0011",
    word: "Good",
    category: "Expression",
    type: "Positive",
    desc: "Flat hand moves from chin downward positively.",
    icon: ThumbsUp,
    tag: null,
  },
  {
    id: "#0012",
    word: "House",
    category: "Place",
    type: "Daily",
    desc: "Hands form roof shape.",
    icon: Home,
    tag: null,
  },
  {
    id: "#0013",
    word: "I",
    category: "Pronoun",
    type: "Personal",
    desc: "Index finger points to chest.",
    icon: User,
    tag: "Common",
  },
  {
    id: "#0014",
    word: "ILoveYou",
    category: "Expression",
    type: "Emotion",
    desc: "Thumb, index and little finger extended.",
    icon: Heart,
    tag: "Common",
  },
  {
    id: "#0015",
    word: "Namaste",
    category: "Greeting",
    type: "Respectful",
    desc: "Hands pressed together with slight bow.",
    icon: Handshake,
    tag: "Common",
  },
  {
    id: "#0016",
    word: "Son",
    category: "Family",
    type: "Relation",
    desc: "Boy sign followed by child sign.",
    icon: Users,
    tag: null,
  },
];

const Dictionary = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('All Entries');

    const filteredData = DICTIONARY_DATA.filter(item => {
        const matchesSearch = item.word.toLowerCase().includes(searchTerm.toLowerCase()) || item.desc.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = categoryFilter === 'All Entries' || item.category === categoryFilter;
        return matchesSearch && matchesCategory;
    });

    return (
        <div className="w-full">
            <div className="w-full text-center space-y-4 mb-16">
                <div className="inline-block px-4 py-1 border-y border-crimson text-crimson text-xs font-bold uppercase tracking-[0.3em] mb-2">
                    Official Corpus
                </div>
                <h2 className="text-4xl md:text-5xl font-serif text-charcoal font-bold tracking-tight">
                    Standardized <span className="italic text-crimson">Sign Lexicon</span>
                </h2>
                <p className="text-stone-500 max-w-2xl mx-auto font-light text-lg">
                    Browse the complete collection of academic Indian Sign Language gestures currently recognized by our neural engine.
                </p>
            </div>

            {/* Search Bar */}
            <div className="w-full max-w-4xl mb-12 relative z-20 mx-auto">
                <div className="bg-white p-1 shadow-sm border border-stone-200 flex items-center rounded-sm">
                    <div className="pl-4 pr-2 text-stone-400">
                        <Search className="w-5 h-5" />
                    </div>
                    <input
                        className="flex-grow border-none focus:ring-0 text-charcoal placeholder-stone-400 font-serif text-lg py-3 focus:outline-none ml-2"
                        placeholder="Search by English word or concept..."
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <div className="hidden sm:flex items-center gap-2 border-l border-stone-200 pl-4 pr-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-stone-400">Category:</span>
                        <select
                            className="border-none focus:ring-0 text-sm font-medium text-charcoal cursor-pointer bg-transparent py-2 pl-2 pr-8 focus:outline-none"
                            value={categoryFilter}
                            onChange={(e) => setCategoryFilter(e.target.value)}
                        >
                            <option>All Entries</option>
                            <option>Travel</option>
                            <option>Time</option>
                            <option>Expression</option>
                            <option>Object</option>
                            <option>Transport</option>
                            <option>Family</option>
                            <option>Daily Life</option>
                            <option>Place</option>
                            <option>Pronoun</option>
                            <option>Greeting</option>
                        </select>
                    </div>
                    <button className="bg-charcoal text-white px-8 py-3 hover:bg-crimson transition-colors font-medium tracking-wide">
                        Find
                    </button>
                </div>
                <div className="flex justify-between items-center mt-3 text-xs text-stone-400 px-2 font-medium uppercase tracking-widest">
                    <span>Displaying {filteredData.length} of {DICTIONARY_DATA.length} Entries</span>
                    <div className="flex gap-4">
                        <button className="hover:text-crimson transition-colors">A-Z</button>
                        <button className="hover:text-crimson transition-colors">Newest</button>
                    </div>
                </div>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full mb-16">
                {filteredData.map((item) => {
                    const Icon = item.icon;
                    return (
                        <div key={item.id} className="glass-panel group cursor-pointer flex flex-col h-full bg-white">
                            {/* <div className="card-thumbnail aspect-[4/3] bg-stone-100 w-full relative">
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <Icon className="w-12 h-12 text-stone-300" />
                                </div>
                                {item.tag && (
                                    <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-crimson shadow-sm">
                                        {item.tag}
                                    </div>
                                )}
                            </div> */}
                            <div className="p-6 flex flex-col flex-grow">
                                <h3 className="text-2xl font-serif font-bold text-charcoal mb-1 group-hover:text-crimson transition-colors">{item.word}</h3>
                                <p className="text-xs text-stone-400 uppercase tracking-widest mb-4">{item.category} • {item.type}</p>
                                <p className="text-sm text-stone-600 line-clamp-2 mb-4">{item.desc}</p>
                                <div className="mt-auto pt-4 border-t border-stone-100 flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-stone-400">ID: {item.id}</span>
                                    <span className="text-crimson text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-[-10px] group-hover:translate-x-0 duration-300">→</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Dictionary;
