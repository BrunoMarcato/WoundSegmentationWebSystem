<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6" v-for="(grupo, index) in grupos" :key="grupo.id">
        <v-card class="mb-4">
          <v-card-title>
            <span class="text-h6">Grupo {{ index + 1 }}</span>
          </v-card-title>

          <v-card-text>
            <v-row>
              <v-col v-for="(img, j) in grupo.images" :key="j" cols="6">
                <v-img :src="img.original" height="100px" cover class="cursor-pointer" @click="expandirImagem(img)" />
                <div class="text-caption mt-1">{{ img.name }}</div>
                <div class="text-caption">Área: {{ img.area }} px²</div>
                <div class="text-caption">Data: {{ img.data }}</div>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-btn icon color="error" size="small" @click="excluirGrupo(index)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
            <v-btn color="primary" size="small" @click="abrirGrafico(grupo)">
              Gerar Gráfico
            </v-btn>
            <v-btn color="success" size="small" @click="baixarGrupo(grupo, index)">
              Baixar Grupo
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-divider class="my-8" />

    <h2 class="text-h5 mb-4">Imagens Segmentadas</h2>

    <v-row>
      <v-col v-for="(img, index) in allResults" :key="index" cols="12" md="3">
        <v-card>
          <v-img :src="img.original" height="150px" cover class="cursor-pointer" @click="expandirImagem(img)" />
          <v-card-text class="text-caption">
            {{ img.name }}<br>
            Área: {{ img.area }} px²<br>
            Data: {{ img.data }}
          </v-card-text>
          <v-card-actions>
            <v-btn small color="primary" @click="toggleSelecionado(index)">
              {{ selected.includes(index) ? "Selecionado" : "Selecionar" }}
            </v-btn>
            <v-btn small color="error" @click="excluirImagem(index)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-btn class="mt-6" color="success" @click="criarGrupo" :disabled="selected.length === 0">
      Criar Grupo
    </v-btn>

    <GraphModal v-if="showGraph" :group="selectedGroup" :show="showGraph"
      @update:show="(val) => { showGraph = val; if (!val) selectedGroup = null }" />

    <!-- Visualização Expandida -->
    <v-dialog v-model="mostrarDialog" max-width="800" transition="dialog-bottom-transition">
      <v-card>
        <v-card-title class="text-h6">
          Visualização: {{ imagemExpandida?.name }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <v-img :src="imagemExpandida?.original" height="300" cover />
              <div class="text-caption mt-2 text-center">Imagem Original</div>
            </v-col>
            <v-col cols="6">
              <v-img :src="'data:image/png;base64,' + imagemExpandida?.mask" height="300" cover />
              <div class="text-caption mt-2 text-center">Máscara Segmentada</div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="mostrarDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar" :timeout="3000" :color="snackbarColor">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-container>
</template>

<script>
import axios from "axios"
import GraphModal from "../components/GraphModal.vue"

export default {
  components: {
    GraphModal
  },
  data() {
    return {
      allResults: [],
      selected: [],
      grupos: [],
      showGraph: false,
      selectedGroup: null,
      snackbar: false,
      snackbarMessage: "",
      snackbarColor: "success",
      imagemExpandida: null,
      mostrarDialog: false
    }
  },
  async mounted() {
    try {
      const segmentacoes = await axios.get("http://localhost:5000/segmentations")
      this.allResults = segmentacoes.data

      const grupos = await axios.get("http://localhost:5000/groups")
      this.grupos = grupos.data
    } catch (e) {
      console.error("Erro ao carregar dados:", e)
    }
  },
  methods: {
    toggleSelecionado(index) {
      if (this.selected.includes(index)) {
        this.selected = this.selected.filter(i => i !== index)
      } else {
        this.selected.push(index)
      }
    },
    async criarGrupo() {
      const imagensSelecionadas = this.selected.map(i => this.allResults[i])

      try {
        const response = await axios.post("http://localhost:5000/groups", {
          images: imagensSelecionadas
        })
        this.grupos.push(response.data.group)
        this.selected = []
      } catch (e) {
        console.error("Erro ao criar grupo:", e)
      }
    },
    async excluirImagem(index) {
      const imagem = this.allResults[index]
      try {
        await axios.delete(`http://localhost:5000/segmentations/${imagem.name}`)
        this.allResults.splice(index, 1)
        this.selected = this.selected.filter(i => i !== index)
      } catch (e) {
        console.error("Erro ao excluir imagem:", e)
      }
    },
    async excluirGrupo(index) {
      const grupo = this.grupos[index]
      try {
        await axios.delete(`http://localhost:5000/groups/${grupo.id}`)
        this.grupos.splice(index, 1)
      } catch (e) {
        console.error("Erro ao excluir grupo:", e)
      }
    },
    abrirGrafico(grupo) {
      this.selectedGroup = grupo
      this.showGraph = true
    },
    expandirImagem(img) {
      this.imagemExpandida = img
      this.mostrarDialog = true
    },
    async baixarGrupo(grupo, index) {
      try {
        const response = await axios.get(`http://localhost:5000/groups/${grupo.id}/download`, {
          responseType: 'blob'
        })

        const blob = new Blob([response.data], { type: "application/zip" })
        const link = document.createElement("a")
        link.href = URL.createObjectURL(blob)
        link.download = `grupo_${index + 1}.zip`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        this.snackbarColor = "success"
        this.snackbarMessage = `Grupo ${grupo.id} baixado com sucesso!`
        this.snackbar = true

      } catch (error) {
        console.error("Erro ao baixar grupo:", error)
        this.snackbarColor = "error"
        this.snackbarMessage = `Erro ao baixar grupo ${grupo.id}`
        this.snackbar = true
      }
    },

    dataURLtoBlob(dataURL) {
      const parts = dataURL.split(',')
      const mime = parts[0].match(/:(.*?);/)[1]
      const bstr = atob(parts[1])
      let n = bstr.length
      const u8arr = new Uint8Array(n)
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n)
      }
      return new Blob([u8arr], { type: mime })
    }
  }
}
</script>
