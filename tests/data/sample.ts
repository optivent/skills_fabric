/**
 * Sample TypeScript module for tree-sitter parsing tests.
 *
 * Contains interfaces, classes, functions, and various TypeScript patterns.
 */

/**
 * User interface representing a system user.
 */
export interface User {
    id: number;
    name: string;
    email?: string;
    role: UserRole;
    createdAt: Date;
}

/**
 * Available user roles in the system.
 */
export type UserRole = "admin" | "user" | "guest" | "moderator";

/**
 * Configuration options for the UserService.
 */
export interface UserServiceConfig {
    apiUrl: string;
    timeout?: number;
    retryCount?: number;
}

/**
 * Service class for managing users.
 *
 * Provides CRUD operations and user management functionality.
 */
export class UserService {
    private users: Map<number, User> = new Map();
    private readonly config: UserServiceConfig;

    /**
     * Create a new UserService instance.
     * @param config - Service configuration options
     */
    constructor(config: UserServiceConfig) {
        this.config = config;
    }

    /**
     * Get a user by their ID.
     * @param id - The user's unique identifier
     * @returns The user if found, undefined otherwise
     */
    async getUser(id: number): Promise<User | undefined> {
        return this.users.get(id);
    }

    /**
     * Create a new user in the system.
     * @param name - The user's name
     * @param email - Optional email address
     * @param role - The user's role (defaults to "user")
     * @returns The newly created user
     */
    async createUser(
        name: string,
        email?: string,
        role: UserRole = "user"
    ): Promise<User> {
        const id = this.users.size + 1;
        const user: User = {
            id,
            name,
            email,
            role,
            createdAt: new Date(),
        };
        this.users.set(id, user);
        return user;
    }

    /**
     * Update an existing user.
     * @param id - The user's ID
     * @param updates - Partial user data to update
     * @returns The updated user if found
     */
    async updateUser(
        id: number,
        updates: Partial<Omit<User, "id" | "createdAt">>
    ): Promise<User | undefined> {
        const user = this.users.get(id);
        if (!user) return undefined;

        const updatedUser = { ...user, ...updates };
        this.users.set(id, updatedUser);
        return updatedUser;
    }

    /**
     * Delete a user from the system.
     * @param id - The user's ID
     * @returns True if the user was deleted
     */
    async deleteUser(id: number): Promise<boolean> {
        return this.users.delete(id);
    }

    /**
     * Get all users matching a role.
     * @param role - The role to filter by
     * @returns Array of users with the specified role
     */
    getUsersByRole(role: UserRole): User[] {
        return Array.from(this.users.values()).filter(
            (user) => user.role === role
        );
    }

    /**
     * Validate an email address format.
     * @param email - The email to validate
     * @returns True if the email format is valid
     */
    static validateEmail(email: string): boolean {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Get the total number of users.
     */
    get userCount(): number {
        return this.users.size;
    }

    /**
     * Check if the service has any users.
     */
    get isEmpty(): boolean {
        return this.users.size === 0;
    }
}

/**
 * Format a user for display.
 * @param user - The user to format
 * @returns Formatted string representation
 */
export function formatUser(user: User): string {
    const email = user.email ?? "no email";
    return `${user.name} <${email}> (${user.role})`;
}

/**
 * Create a guest user with minimal information.
 * @param name - The guest's name
 * @returns A new guest user object
 */
export function createGuestUser(name: string): User {
    return {
        id: Date.now(),
        name,
        role: "guest",
        createdAt: new Date(),
    };
}

/**
 * Arrow function to check if a user is an admin.
 */
export const isAdmin = (user: User): boolean => user.role === "admin";

/**
 * Arrow function to get user initials.
 */
export const getUserInitials = (user: User): string =>
    user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase();

/**
 * Default role for new users.
 */
export const DEFAULT_ROLE: UserRole = "user";

/**
 * Default timeout for API requests (in milliseconds).
 */
export const DEFAULT_TIMEOUT = 30000;
