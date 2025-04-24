# React Coding Standards Guide

This guide outlines comprehensive standards for writing clean, maintainable, and production-ready React applications. It covers best practices, conventions, and patterns to ensure consistent, high-quality code.

## Table of Contents
- [Project Structure](#project-structure)
- [Component Architecture](#component-architecture)
- [Naming Conventions](#naming-conventions)
- [Props and Type Checking](#props-and-type-checking)
- [Hooks and State Management](#hooks-and-state-management)
- [Performance Optimization](#performance-optimization)
- [Styling Approaches](#styling-approaches)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Accessibility](#accessibility)
- [Security Best Practices](#security-best-practices)
- [Code Quality Tools](#code-quality-tools)
- [Common Anti-patterns](#common-anti-patterns)

## Project Structure

### Recommended Directory Structure
```
src/
├── assets/                  # Static files like images, fonts
├── components/              # Reusable components
│   ├── ui/                  # Primitive UI components 
│   ├── layout/              # Layout components
│   └── features/            # Feature-specific components
├── hooks/                   # Custom hooks
├── context/                 # React context definitions
├── pages/                   # Page components (for routing)
├── services/                # API calls and external services
├── utils/                   # Utility functions
├── constants/               # Application constants
├── types/                   # TypeScript type definitions
├── styles/                  # Global styles and themes
└── App.jsx                  # Root component
```

### Module Organization
- Group related files (component, styles, tests, types) together
- For complex features, use a feature-based organization:
  ```
  features/
  ├── authentication/
  │   ├── components/
  │   ├── hooks/
  │   ├── services/
  │   └── index.js           # Public API of the feature
  └── dashboard/
      └── ...
  ```

### Import/Export Conventions
- Use named exports for most components and utilities
- Reserve default exports for main entry points of a module or component
- Use barrel exports (index.js files) to simplify imports:

```jsx
// In components/ui/index.js
export { Button } from './Button';
export { Input } from './Input';

// In consumer files
import { Button, Input } from 'components/ui';
```

## Component Architecture

### Component Types
1. **Presentational Components**
   - Focus on UI rendering with minimal logic
   - Receive data via props
   - Should be highly reusable

2. **Container Components**
   - Handle data fetching and state management
   - Pass data to presentational components

3. **Layout Components**
   - Manage page structure and positioning
   - Examples: Header, Footer, Sidebar

4. **Page Components**
   - Correspond to routes in the application
   - Compose multiple components together

### Component Composition Patterns

#### Use Composition Over Props Drilling
```jsx
// ❌ Avoid:
<Table data={data} onRowClick={onRowClick} showActions={true} />

// ✅ Better:
<Table data={data}>
  <Table.Row onClick={onRowClick}>
    <Table.Cell>
      <Actions />
    </Table.Cell>
  </Table.Row>
</Table>
```

#### Use Render Props and HOCs Sparingly
Prefer hooks for shared logic when possible.

```jsx
// HOC example (use sparingly)
function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const isAuthenticated = useAuth();
    if (!isAuthenticated) return <Redirect to="/login" />;
    return <Component {...props} />;
  };
}

// Prefer hook approach
function ProtectedRoute({ children }) {
  const isAuthenticated = useAuth();
  if (!isAuthenticated) return <Redirect to="/login" />;
  return children;
}
```

### File Organization
- One component per file (except for small, tightly coupled components)
- Match file names with component names
- Group related files:
  ```
  Button/
  ├── Button.jsx
  ├── Button.test.jsx
  ├── Button.module.css
  └── index.js
  ```

## Naming Conventions

### Components
- Use PascalCase for component names
- Name files the same as the component they contain
- Be descriptive but concise

```jsx
// ✅ Good component names
UserProfile.jsx
PaymentForm.jsx
NavigationBar.jsx

// ❌ Bad component names
Comp.jsx
Page.jsx
Form.jsx
```

### Props
- Use camelCase for prop names
- Boolean props should have "is", "has", or "should" prefix
- Event handler props should start with "on" followed by the event name

```jsx
// ✅ Good prop names
<Button 
  isDisabled={true}
  onClick={handleClick}
  backgroundColor="blue"
/>

// ❌ Bad prop names
<Button 
  disabled={true}
  clickHandler={handleClick}
  background-color="blue"
/>
```

### CSS Classes
- Use kebab-case for CSS class names
- Use module CSS or a naming convention like BEM to avoid collisions

```css
/* With CSS Modules */
.button-primary {
  color: white;
  background-color: blue;
}

/* With BEM */
.button--primary {
  color: white;
  background-color: blue;
}
```

### Custom Hooks
- Always start custom hook names with "use"
- Name should describe what the hook does

```jsx
// ✅ Good hook names
useWindowSize()
useFetchData()
useFormValidation()

// ❌ Bad hook names
windowSize()
getData()
formHook()
```

## Props and Type Checking

### PropTypes
When using PropTypes for runtime validation:

```jsx
import PropTypes from 'prop-types';

function Button({ label, onClick, isDisabled }) {
  return (
    <button onClick={onClick} disabled={isDisabled}>
      {label}
    </button>
  );
}

Button.propTypes = {
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool
};

Button.defaultProps = {
  isDisabled: false
};
```

### TypeScript
When using TypeScript (preferred for larger applications):

```tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
  isDisabled?: boolean;
}

function Button({ label, onClick, isDisabled = false }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={isDisabled}>
      {label}
    </button>
  );
}
```

### Props Best Practices
- Destructure props in the function signature
- Provide default values for optional props
- Avoid excessive props (consider splitting the component)
- Use object spread for passing props to DOM elements cautiously

```jsx
// ✅ Good: Destructuring with defaults
function Button({ label, onClick, type = "button", isDisabled = false }) {
  // Component code
}

// ❌ Avoid: Using object spread without filtering irrelevant props
function Button(props) {
  return <button {...props}>Click me</button>; // Might pass irrelevant/unsafe props
}

// ✅ Better: Explicitly spreading allowed props
function Button(props) {
  const { className, children, ...restProps } = props;
  const allowedProps = ['onClick', 'type', 'disabled'].reduce((acc, key) => {
    if (key in restProps) acc[key] = restProps[key];
    return acc;
  }, {});
  
  return <button className={className} {...allowedProps}>{children}</button>;
}
```

## Hooks and State Management

### useState
- Group related state variables or use objects for complex state
- Use functional updates for state that depends on previous value

```jsx
// ✅ Good: Functional updates
const [count, setCount] = useState(0);
setCount(prevCount => prevCount + 1);

// ✅ Good: Object state for related values
const [form, setForm] = useState({ name: '', email: '', password: '' });
setForm(prevForm => ({ ...prevForm, name: 'John' }));
```

### useEffect
- Keep effects focused on a single concern
- Avoid unnecessary dependencies
- Cleanup properly to prevent memory leaks

```jsx
// ✅ Good: Single concern with proper cleanup
useEffect(() => {
  const subscription = api.subscribe(data => {
    setData(data);
  });
  
  return () => {
    subscription.unsubscribe();
  };
}, [api]); // Only dep is the api object
```

### Custom Hooks
- Create custom hooks to share logic between components
- Name them descriptively and start with "use"
- Keep them focused on a specific functionality

```jsx
// ✅ Good: Custom hook for form handling
function useForm(initialValues) {
  const [values, setValues] = useState(initialValues);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };
  
  const reset = () => setValues(initialValues);
  
  return { values, handleChange, reset };
}

// Usage
function SignupForm() {
  const { values, handleChange, reset } = useForm({ email: '', password: '' });
  // Rest of component
}
```

### Context API
- Use for truly global state (theme, user auth, etc.)
- Create separate contexts for different domains
- Provide a custom hook to consume each context

```jsx
// Creating a context
const UserContext = createContext();

function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  const login = async (credentials) => {
    // Login logic
  };
  
  const logout = () => {
    // Logout logic
  };
  
  return (
    <UserContext.Provider value={{ user, login, logout }}>
      {children}
    </UserContext.Provider>
  );
}

// Custom hook to use the context
function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

// Usage in components
function Profile() {
  const { user, logout } = useUser();
  // Component code
}
```

### External State Management
For complex applications, consider well-established libraries:

- Redux/Redux Toolkit for global state with complex interactions
- Zustand for simpler global state
- React Query/SWR for server state and data fetching
- Jotai/Recoil for atom-based state management

## Performance Optimization

### Memoization
- Use `React.memo()` for components that render often with the same props
- Use `useMemo()` for expensive calculations
- Use `useCallback()` for functions passed to optimized child components

```jsx
// ✅ Good: Memoizing expensive calculation
const memoizedValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

// ✅ Good: Memoizing callback for optimized children
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);

// ✅ Good: Preventing unnecessary re-renders
const MemoizedComponent = React.memo(function MyComponent(props) {
  // component implementation
});
```

### Virtual Lists
- Use virtualization for long lists (`react-window` or `react-virtualized`)

```jsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );

  return (
    <FixedSizeList
      height={500}
      width="100%"
      itemCount={items.length}
      itemSize={35}
    >
      {Row}
    </FixedSizeList>
  );
}
```

### Code Splitting
- Use dynamic imports for route-based code splitting

```jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Dashboard />
    </Suspense>
  );
}
```

### Additional Performance Tips
- Use production builds for deployment
- Implement proper key usage in lists (unique, stable IDs)
- Avoid anonymous functions in render where possible
- Consider server-side rendering or static generation for better initial load performance

## Styling Approaches

### CSS-in-JS
Libraries like styled-components or emotion:

```jsx
// styled-components example
import styled from 'styled-components';

const Button = styled.button`
  background-color: ${props => props.primary ? 'blue' : 'white'};
  color: ${props => props.primary ? 'white' : 'blue'};
  padding: 8px 16px;
  border-radius: 4px;
`;

function MyComponent() {
  return <Button primary>Click Me</Button>;
}
```

### CSS Modules
```jsx
// Button.module.css
.button {
  padding: 8px 16px;
  border-radius: 4px;
}

.primary {
  background-color: blue;
  color: white;
}

// Button.jsx
import styles from './Button.module.css';

function Button({ children, isPrimary }) {
  return (
    <button className={`${styles.button} ${isPrimary ? styles.primary : ''}`}>
      {children}
    </button>
  );
}
```

### Utility-First CSS (Tailwind)
```jsx
function Button({ children, isPrimary }) {
  return (
    <button className={`px-4 py-2 rounded ${
      isPrimary ? 'bg-blue-500 text-white' : 'bg-white text-blue-500'
    }`}>
      {children}
    </button>
  );
}
```

### Styling Best Practices
- Be consistent with your chosen styling approach
- Consider component-level styling over global styles
- Use CSS variables for theming and reusable values
- Create a design system with reusable components and consistent styling
- Consider responsive design and accessibility in your styling

## Testing

### Component Testing
Using Jest and React Testing Library:

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
  test('renders with correct label', () => {
    render(<Button label="Click me" onClick={() => {}} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button label="Click me" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('is disabled when isDisabled prop is true', () => {
    render(<Button label="Click me" onClick={() => {}} isDisabled={true} />);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

### Hook Testing
```jsx
import { renderHook, act } from '@testing-library/react-hooks';
import useCounter from './useCounter';

describe('useCounter', () => {
  test('should increment counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
});
```

### Testing Best Practices
- Focus on testing behavior, not implementation details
- Write tests that resemble how users interact with components
- Test accessibility where appropriate
- Use meaningful assertions and test descriptions
- Mock external dependencies when necessary
- Use data-testid attributes sparingly, prefer accessible roles and text content
- Implement integration tests for key user flows
- Consider implementing end-to-end tests for critical paths

## Error Handling

### Error Boundaries
```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### Async Error Handling
```jsx
function ProfilePage() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        setIsLoading(true);
        const response = await fetchUserData(userId);
        setUser(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchUser();
  }, [userId]);

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage message={error.message} />;
  if (!user) return <NotFound />;

  return <UserProfile user={user} />;
}
```

### Form Validation Errors
```jsx
function SignupForm() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!form.email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!form.password) newErrors.password = 'Password is required';
    else if (form.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Submit form
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          type="email"
          value={form.email}
          onChange={(e) => setForm({...form, email: e.target.value})}
          aria-invalid={errors.email ? "true" : "false"}
        />
        {errors.email && <p role="alert">{errors.email}</p>}
      </div>
      {/* Other form fields */}
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

## Accessibility

### Semantic HTML
- Use proper HTML elements for their intended purpose
- Structure content with appropriate heading levels (h1-h6)
- Use landmarks (main, nav, header, footer, etc.)

```jsx
// ✅ Good: Semantic HTML
function Article({ title, content }) {
  return (
    <article>
      <h2>{title}</h2>
      <p>{content}</p>
    </article>
  );
}

// ❌ Bad: Divs for everything
function Article({ title, content }) {
  return (
    <div className="article">
      <div className="title">{title}</div>
      <div className="content">{content}</div>
    </div>
  );
}
```

### ARIA Attributes
- Use ARIA roles, states, and properties when HTML semantics aren't sufficient
- Keep ARIA usage minimal: "No ARIA is better than bad ARIA"

```jsx
// Custom dropdown example
function Dropdown({ label, options, selected, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div>
      <button
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
      >
        {selected || label}
      </button>
      
      {isOpen && (
        <ul role="listbox" aria-labelledby="dropdown-label">
          {options.map(option => (
            <li
              key={option.value}
              role="option"
              aria-selected={selected === option.value}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Keyboard Navigation
- Ensure all interactive elements are keyboard accessible
- Implement proper focus management
- Use tabIndex appropriately

```jsx
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef();
  
  useEffect(() => {
    if (isOpen) {
      // Store the active element to restore focus later
      const activeElement = document.activeElement;
      
      // Focus the modal when it opens
      modalRef.current.focus();
      
      return () => {
        // Restore focus when modal closes
        activeElement.focus();
      };
    }
  }, [isOpen]);
  
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal"
        ref={modalRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        onClick={e => e.stopPropagation()}
      >
        <button 
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>
        {children}
      </div>
    </div>
  );
}
```

### Color and Contrast
- Ensure sufficient color contrast (WCAG AA: 4.5:1 for normal text)
- Don't rely solely on color to convey information
- Support high contrast mode

### Accessibility Testing
- Use tools like axe-core, pa11y, or Lighthouse
- Test with screen readers
- Implement keyboard navigation testing

## Security Best Practices

### XSS Prevention
- Avoid using dangerouslySetInnerHTML
- When necessary, sanitize content first:

```jsx
import DOMPurify from 'dompurify';

function SafeHTML({ content }) {
  return (
    <div 
      dangerouslySetInnerHTML={{
        __html: DOMPurify.sanitize(content)
      }}
    />
  );
}
```

### Safe URL Handling
```jsx
// ✅ Good: URL validation
function LinkButton({ url, children }) {
  // Only allow http:, https: and mailto: protocols
  const isSafeUrl = /^(?:https?:|mailto:)/i.test(url);
  
  if (!isSafeUrl) {
    return <span>{children}</span>;
  }
  
  return (
    <a href={url} rel="noopener noreferrer">
      {children}
    </a>
  );
}
```

### Authentication Best Practices
- Store tokens securely (httpOnly cookies preferred over localStorage)
- Implement proper logout mechanisms
- Use secure, time-limited tokens
- Implement CSRF protection for cookie-based auth

### User Input Validation
- Validate both client-side and server-side
- Sanitize user inputs before rendering or storing
- Use controlled components for forms

## Code Quality Tools

### ESLint
```json
// .eslintrc.json example
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": [
    "react",
    "react-hooks",
    "jsx-a11y"
  ],
  "rules": {
    "react/prop-types": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": "warn"
  }
}
```

### Prettier
```json
// .prettierrc example
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "bracketSpacing": true,
  "jsxBracketSameLine": false
}
```

### Git Hooks
Use husky and lint-staged to enforce code quality on commit:

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

## Common Anti-patterns

### Rendering Issues
- ❌ **Avoid**: Direct DOM manipulation in React components
- ❌ **Avoid**: Using indexes as keys in lists
- ❌ **Avoid**: Complex calculations in render methods
- ❌ **Avoid**: Nested ternary operators

### State Management Issues
- ❌ **Avoid**: Updating state based on props without useEffect
- ❌ **Avoid**: Mutating state directly
- ❌ **Avoid**: Excessive prop drilling
- ❌ **Avoid**: Using state for values that can be computed

### Performance Issues
- ❌ **Avoid**: Creating functions inside render
- ❌ **Avoid**: Unnecessary re-renders
- ❌ **Avoid**: Overusing Context for everything
- ❌ **Avoid**: Heavy computations without memoization

### Hook Usage Issues
- ❌ **Avoid**: Using hooks conditionally
- ❌ **Avoid**: Using useState when useReducer would be clearer
- ❌ **Avoid**: Missing dependencies in useEffect
- ❌ **Avoid**: Over-dependency on useEffect for related state updates

## Recommended Patterns

### Custom Hook for API Calls
```jsx
function useApi(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        const json = await response.json();
        
        if (isMounted) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setData(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [url]);

  return { data, error, loading };
}
```

### Component Composition Pattern
```jsx
// Button component with variants
function Button({ children, variant = 'primary', size = 'medium', ...props }) {
  const variantClasses = {
    primary: 'bg-blue-500 text-white',
    secondary: 'bg-gray-200 text-gray-800',
    danger: 'bg-red-500 text-white',
  };
  
  const sizeClasses = {
    small: 'px-2 py-1 text-sm',
    medium: 'px-4 py-2',
    large: 'px-6 py-3 text-lg',
  };
  
  const className = `${variantClasses[variant]} ${sizeClasses[size]} rounded`;
  
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
}

// Icon button extension
function IconButton({ icon, children, ...props }) {
  return (
    <Button {...props}>
      <span className="mr-2">{icon}</span>
      {children}
    </Button>
  );
}
```

### Form Handling Pattern
```jsx
function useForm(initialValues) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };
  
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  };
  
  const validate = (validationSchema) => {
    const newErrors = {};
    Object.keys(validationSchema).forEach(field => {
      const value = values[field];
      const validators = validationSchema[field];
      
      for (const validator of validators) {
        const error = validator(value);
        if (error) {
          newErrors[field] = error;
          break;
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };
  
  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    reset
  };
}
```

---

By following these standards, LLMs can generate React code that is clean, maintainable, performant, and production-ready. This guide covers the essential aspects of modern React development with a focus on best practices that lead to scalable applications.
