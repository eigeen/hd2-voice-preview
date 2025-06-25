<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from "vue";
import { useQuery } from "@pinia/colada";
import { DataSource } from "./api";
import { useRoute, useRouter } from "vue-router";

interface VoiceItem {
  id: string;
  content: string;
  file: string;
}

const VOICE_BASE_URL = "https://os1.eigeen.com/hd2-voice-preview/";

// 分类和音效数据
const { state: categoriesState } = useQuery({
  key: ["categories"],
  query: () => DataSource.getCategories(),
});
const route = useRoute();
const router = useRouter();
const selectedCategory = ref("");
const itemsPerPage = ref<number>(-1);
const playingFile = ref<string | null>(null);
let audioInstance: HTMLAudioElement | null = null;
const volume = ref(1);
const highlightedId = ref<string | null>(null);
const toScroll = ref(true);
const showMessage = ref(false);

const TRUNCATE_LENGTH = 8; // ID显示的前N位数

// 监听路由hash变化
watch(
  () => route.hash,
  (newHash) => {
    highlightedId.value = newHash ? newHash.slice(1) : null;
    if (highlightedId.value) {
      toScroll.value = true;
    }
  },
  { immediate: true },
);

// 路由变化时同步selectedCategory
watch(
  () => route.params.category,
  (val) => {
    if (val && val !== selectedCategory.value) {
      selectedCategory.value = val as string;
    }
  },
  { immediate: true },
);

// 切换分类时跳转路由
watch(selectedCategory, (val) => {
  if (!val) return;

  if (val !== route.params.category) {
    router.replace({ name: "home", params: { category: val } });
  }
  stopAudio();
});

watch(volume, (val) => {
  if (audioInstance) {
    audioInstance.volume = val;
  }
});

const header = [
  { title: "ID", key: "id" },
  { title: "内容", key: "content" },
  {
    title: "操作",
    key: "actions",
    sortable: false,
    fixed: true,
    align: "end" as const,
    minWidth: "100px",
  },
];

const sheetData = useQuery({
  key: () => ["sheetData", selectedCategory.value],
  query: () => {
    toScroll.value = true;
    return DataSource.getManifest(selectedCategory.value);
  },
});

// 滚动到高亮行
async function scrollToHighlightedRow() {
  nextTick(() => {
    const highlightedRow = document.querySelector(".highlighted-row");
    if (highlightedRow) {
      highlightedRow.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
}

async function stopAudio() {
  if (audioInstance) {
    audioInstance.pause();
    audioInstance.currentTime = 0;
    audioInstance = null;
  }
  playingFile.value = null;
}

async function handlePlaySound(file: string) {
  const url = `${VOICE_BASE_URL}/${selectedCategory.value}/${file}`;
  // 如果正在播放当前音频，则停止
  if (playingFile.value === file) {
    await stopAudio();
    return;
  }

  // 如果有其他音频在播放，先停止
  await stopAudio();
  audioInstance = new Audio(url);
  audioInstance.volume = volume.value;
  audioInstance.onended = () => {
    playingFile.value = null;
    audioInstance = null;
  };
  playingFile.value = file;
  await audioInstance.play();
}

async function shareSound(file: string) {
  const audioId = file.split(".")[0];
  // 更新路由hash，保持当前路径不变
  await router.replace({
    path: route.path,
    hash: `#${audioId}`,
  });
  // 复制URL到剪贴板
  const url = window.location.href;
  await navigator.clipboard.writeText(url);
  // 显示提示消息
  showMessage.value = true;
  setTimeout(() => {
    showMessage.value = false;
  }, 2000);
}

function isHighlighted(item: VoiceItem) {
  return highlightedId.value === item.file.split(".")[0];
}

// 添加复制ID到剪贴板的函数
async function copyId(id: string) {
  await navigator.clipboard.writeText(id);
  showMessage.value = true;
  setTimeout(() => {
    showMessage.value = false;
  }, 2000);
}

onMounted(() => {
  const scrollInterval = setInterval(() => {
    if (toScroll.value && highlightedId.value) {
      toScroll.value = false;
      scrollToHighlightedRow();
    }
  }, 500);

  return () => {
    clearInterval(scrollInterval);
  };
});
</script>

<template>
  <v-app>
    <v-container
      class="py-6"
      style="max-width: 800px"
    >
      <v-row>
        <v-col cols="12">
          <v-autocomplete
            v-model="selectedCategory"
            :items="categoriesState.data || []"
            item-title="label"
            item-value="value"
            label="选择语音分组"
            hide-details
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <!-- Toolbar -->
          <v-card class="pa-2 mb-2 d-flex items-center">
            <v-slider
              v-model="volume"
              min="0"
              max="1"
              step="0.01"
              hide-details
              label="音量"
              style="max-width: 300px; margin-left: 8px"
            >
              <template #prepend>
                <v-icon>mdi-volume-low</v-icon>
              </template>
              <template #append>
                <v-icon>mdi-volume-high</v-icon>
              </template>
            </v-slider>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="header"
            :items="sheetData.data.value || []"
            class="elevation-1"
            v-model:items-per-page="itemsPerPage"
          >
            <template v-slot:item="{ item }">
              <tr :class="{ 'highlighted-row': isHighlighted(item) }">
                <td>
                  <!-- 桌面端显示完整ID -->
                  <span class="hidden sm:inline">{{ item.id }}</span>
                  <!-- 移动端显示截断的ID -->
                  <span
                    class="sm:hidden cursor-pointer"
                    @click="copyId(item.id)"
                    :title="`点击复制：${item.id}`"
                  >
                    {{ item.id.slice(0, TRUNCATE_LENGTH) }}...
                  </span>
                </td>
                <td>{{ item.content }}</td>
                <td class="text-right">
                  <!-- 桌面端显示 -->
                  <div class="hidden sm:flex justify-end">
                    <v-btn
                      :icon="
                        playingFile === item.file ? 'mdi-stop' : 'mdi-play'
                      "
                      size="small"
                      variant="text"
                      @click="handlePlaySound(item.file)"
                    ></v-btn>
                    <v-btn
                      icon="mdi-share-variant"
                      size="small"
                      variant="text"
                      @click="shareSound(item.file)"
                    ></v-btn>
                  </div>
                  <!-- 移动端显示 -->
                  <div class="sm:hidden">
                    <v-menu>
                      <template v-slot:activator="{ props }">
                        <v-btn
                          icon="mdi-dots-vertical"
                          size="small"
                          variant="text"
                          v-bind="props"
                        ></v-btn>
                      </template>
                      <v-list>
                        <v-list-item @click="handlePlaySound(item.file)">
                          <template v-slot:prepend>
                            <v-icon
                              :icon="
                                playingFile === item.file
                                  ? 'mdi-stop'
                                  : 'mdi-play'
                              "
                              size="small"
                            ></v-icon>
                          </template>
                          <v-list-item-title>
                            {{ playingFile === item.file ? "停止" : "播放" }}
                          </v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="shareSound(item.file)">
                          <template v-slot:prepend>
                            <v-icon
                              icon="mdi-share-variant"
                              size="small"
                            ></v-icon>
                          </template>
                          <v-list-item-title>分享</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
    <!-- 提示消息 -->
    <v-snackbar
      v-model="showMessage"
      :timeout="2000"
      color="success"
      location="top"
    >
      {{ playingFile ? "链接已复制到剪贴板" : "ID已复制到剪贴板" }}
    </v-snackbar>
  </v-app>
</template>

<style scoped>
.highlighted-row {
  background-color: rgba(255, 255, 0, 0.2) !important;
}
.cursor-pointer {
  cursor: pointer;
}
</style>
