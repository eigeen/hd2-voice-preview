export interface CategoryItem {
  label: string;
  value: string;
}

export interface VoiceItem {
  id: string;
  content: string;
  file: string;
}

export class DataSource {
  static async getCategories(): Promise<CategoryItem[]> {
    const response = await fetch("/categories.json");
    return response.json();
  }

  static async getManifest(category: string): Promise<VoiceItem[]> {
    const response = await fetch(`/${category}.json`);
    return response.json();
  }
}
