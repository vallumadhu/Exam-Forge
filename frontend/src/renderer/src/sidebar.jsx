import { Home, Library, Settings, User, PanelLeft } from 'lucide-react';
import { useState } from 'react';
import "./sidebar.css"

export default function Sidebar() {
    const [activeItem, setActiveItem] = useState('home');
    const [isExpanded, setIsExpanded] = useState(true);

    const menuItems = [
        { id: 'home', label: 'Home', icon: Home },
        { id: 'library', label: 'Library', icon: Library },
        { id: 'settings', label: 'Settings', icon: Settings },
        { id: 'account', label: 'Account', icon: User }
    ];

    return (
        <div className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}>
            <button 
                className='sidebar-toggle'
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <PanelLeft size={20} />
            </button>
            <nav className="sidebar-nav">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeItem === item.id;

                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveItem(item.id)}
                            className={`nav-btn ${isActive ? 'active' : ''}`}
                            title={!isExpanded ? item.label : ''}
                        >
                            <Icon size={20} />
                            {isExpanded && <span className="nav-text">{item.label}</span>}
                        </button>
                    );
                })}
            </nav>
        </div>
    );
}