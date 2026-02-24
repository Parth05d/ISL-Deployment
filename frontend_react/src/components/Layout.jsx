import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookOpen } from 'lucide-react';

const Layout = ({ children }) => {
    const location = useLocation();

    const isActive = (path) => {
        return location.pathname === path ? 'text-crimson border-crimson' : 'text-charcoal hover:text-crimson border-transparent hover:border-crimson';
    };

    return (
        <div className="flex flex-col min-h-screen relative overflow-x-hidden">
            <div className="fixed top-0 left-0 w-full h-1 bg-crimson z-50"></div>

            {/* Header */}
            <header className="w-full px-8 py-8 lg:px-16 flex items-center justify-between border-b border-stone-200 bg-cream/80 backdrop-blur-sm sticky top-0 z-40">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-crimson flex items-center justify-center rounded-sm shadow-md">
                        <BookOpen className="text-white w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-charcoal text-2xl font-serif font-bold tracking-tight">ISL Connect</h1>
                        <p className="text-crimson text-[10px] uppercase tracking-[0.2em] font-bold">Lexicon Repository</p>
                    </div>
                </div>

                <nav className="hidden md:flex items-center gap-1">
                    <Link to="/" className={`px-5 py-2 text-sm font-medium transition-colors border-b-2 ${isActive('/')}`}>
                        Home
                    </Link>
                    <Link to="/dictionary" className={`px-5 py-2 text-sm font-medium transition-colors border-b-2 ${isActive('/dictionary')}`}>
                        Dictionary
                    </Link>
                    {/* <a href="#" className="px-5 py-2 text-sm font-medium text-charcoal hover:text-crimson transition-colors border-b-2 border-transparent hover:border-crimson">
                        Practice
                    </a> */}
                </nav>
            </header>

            {/* Main Content */}
            <main className="flex-grow w-full max-w-7xl mx-auto px-6 py-12 flex flex-col items-center">
                {children}
            </main>

            {/* Footer */}
            {/* <footer className="w-full py-12 px-16 mt-auto border-t border-stone-200 flex flex-col md:flex-row justify-between items-center gap-6 bg-white/50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 border border-crimson flex items-center justify-center">
                        <span className="text-crimson font-serif font-bold text-xs">C</span>
                    </div>
                    <span className="font-serif text-sm italic text-stone-500">Cultivating Communication</span>
                </div>
                <div className="flex gap-8 text-[10px] font-bold uppercase tracking-widest text-stone-400">
                    <a href="#" className="hover:text-crimson">Legal</a>
                    <a href="#" className="hover:text-crimson">Ethics</a>
                    <a href="#" className="hover:text-crimson">Foundation</a>
                </div>
                <p className="text-[10px] text-stone-400 font-medium">© 2026 ISL CONNECT RESEARCH INSTITUTE.</p>
            </footer> */}
        </div>
    );
};

export default Layout;
