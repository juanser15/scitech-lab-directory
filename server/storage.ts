import { type User, type InsertUser, type Notification } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getNotifications(): Promise<Notification[]>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private notifications: Notification[];

  constructor() {
    this.users = new Map();
    this.notifications = [
      {
        id: "1",
        title: "GroWise Dashboard Updated",
        message: "Q4 2025 data has been loaded with latest NAV performance metrics.",
        type: "update",
        date: "2025-01-27",
        read: false
      },
      {
        id: "2",
        title: "SigmaLab v2.1 Released",
        message: "New correlation analysis features and improved portfolio optimization.",
        type: "update",
        date: "2025-01-25",
        read: false
      },
      {
        id: "3",
        title: "SciTech University Launched",
        message: "Access courses, certifications and learning resources for quantitative finance.",
        type: "new",
        date: "2025-01-20",
        read: true
      },
      {
        id: "4",
        title: "Atlas Risk Engine Enhanced",
        message: "Added VaR calculations and stress testing scenarios.",
        type: "update",
        date: "2025-01-15",
        read: true
      }
    ];
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getNotifications(): Promise<Notification[]> {
    return this.notifications.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }
}

export const storage = new MemStorage();
