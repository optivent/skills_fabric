/**
 * Sample JavaScript module for tree-sitter parsing tests.
 *
 * Contains classes, functions, and various JavaScript patterns.
 */

/**
 * Event emitter class for pub/sub pattern.
 */
class EventEmitter {
    /**
     * Create a new EventEmitter instance.
     */
    constructor() {
        this.events = {};
        this.maxListeners = 10;
    }

    /**
     * Add an event listener.
     * @param {string} event - Event name
     * @param {Function} listener - Callback function
     * @returns {EventEmitter} This instance for chaining
     */
    on(event, listener) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        if (this.events[event].length >= this.maxListeners) {
            console.warn(`Max listeners (${this.maxListeners}) reached for event: ${event}`);
        }
        this.events[event].push(listener);
        return this;
    }

    /**
     * Add a one-time event listener.
     * @param {string} event - Event name
     * @param {Function} listener - Callback function
     * @returns {EventEmitter} This instance for chaining
     */
    once(event, listener) {
        const wrapper = (...args) => {
            this.off(event, wrapper);
            listener.apply(this, args);
        };
        return this.on(event, wrapper);
    }

    /**
     * Emit an event with arguments.
     * @param {string} event - Event name
     * @param {...*} args - Arguments to pass to listeners
     * @returns {boolean} True if event had listeners
     */
    emit(event, ...args) {
        const listeners = this.events[event];
        if (!listeners || listeners.length === 0) {
            return false;
        }
        listeners.forEach(listener => {
            try {
                listener.apply(this, args);
            } catch (error) {
                console.error(`Error in listener for event ${event}:`, error);
            }
        });
        return true;
    }

    /**
     * Remove an event listener.
     * @param {string} event - Event name
     * @param {Function} listener - Callback to remove
     * @returns {EventEmitter} This instance for chaining
     */
    off(event, listener) {
        const listeners = this.events[event];
        if (listeners) {
            this.events[event] = listeners.filter(l => l !== listener);
        }
        return this;
    }

    /**
     * Remove all listeners for an event (or all events).
     * @param {string} [event] - Optional event name
     * @returns {EventEmitter} This instance for chaining
     */
    removeAllListeners(event) {
        if (event) {
            delete this.events[event];
        } else {
            this.events = {};
        }
        return this;
    }

    /**
     * Get listener count for an event.
     * @param {string} event - Event name
     * @returns {number} Number of listeners
     */
    listenerCount(event) {
        return this.events[event]?.length || 0;
    }
}

/**
 * Data processor class for transforming data.
 */
class DataProcessor {
    /**
     * Create a DataProcessor with options.
     * @param {Object} options - Configuration options
     * @param {boolean} [options.strict=false] - Enable strict mode
     * @param {Function} [options.transform] - Default transform function
     */
    constructor(options = {}) {
        this.options = options;
        this.strict = options.strict ?? false;
        this.transform = options.transform ?? (x => x);
        this.processedCount = 0;
    }

    /**
     * Process an array of items.
     * @param {Array} input - Items to process
     * @returns {Array} Processed items
     */
    process(input) {
        const result = input.map(item => {
            const processed = this.transform(item);
            this.processedCount++;
            return processed;
        });
        return result;
    }

    /**
     * Process items with a custom transform.
     * @param {Array} input - Items to process
     * @param {Function} customTransform - Custom transform function
     * @returns {Array} Processed items
     */
    processWithTransform(input, customTransform) {
        return input.map(customTransform);
    }

    /**
     * Create a processor with default settings.
     * @param {Object} options - Override options
     * @returns {DataProcessor} New processor instance
     */
    static create(options) {
        return new DataProcessor(options);
    }

    /**
     * Get the number of items processed.
     * @returns {number} Processed item count
     */
    get stats() {
        return {
            processedCount: this.processedCount,
            strict: this.strict,
        };
    }
}

// Arrow function - debounce utility
const debounce = (fn, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
};

// Arrow function - throttle utility
const throttle = (fn, limit) => {
    let inThrottle = false;
    return (...args) => {
        if (!inThrottle) {
            fn(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Regular function - memoize utility
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}

// Async function - fetch with retry
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
    let lastError;
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            lastError = error;
            if (i < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
            }
        }
    }
    throw lastError;
}

// Regular function with multiple parameters
function processData(data, options = {}, callback = null) {
    const { filter, sort, limit } = options;

    let result = [...data];

    if (filter) {
        result = result.filter(filter);
    }

    if (sort) {
        result.sort(sort);
    }

    if (limit && limit > 0) {
        result = result.slice(0, limit);
    }

    if (callback) {
        callback(result);
    }

    return result;
}

// Private helper function (convention)
function _validateInput(input) {
    if (!Array.isArray(input)) {
        throw new TypeError('Input must be an array');
    }
    return true;
}

// Module constants
const DEFAULT_OPTIONS = {
    strict: false,
    timeout: 30000,
};

const MAX_RETRY_COUNT = 3;

// Export for CommonJS
module.exports = {
    EventEmitter,
    DataProcessor,
    debounce,
    throttle,
    memoize,
    fetchWithRetry,
    processData,
    DEFAULT_OPTIONS,
    MAX_RETRY_COUNT,
};
