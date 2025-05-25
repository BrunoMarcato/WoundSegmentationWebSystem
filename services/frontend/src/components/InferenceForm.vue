<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Imagem</v-card-title>
          <v-card-text>
            <v-file-input label="Escolha uma imagem" accept="image/*" outlined @change="handleFileChange"
              @click:clear="clearSelectedFile" />


            <v-text-field v-if="selectedFile" v-model="selectedDate" label="Data da imagem" type="date" outlined dense
              class="mt-3" />

            <v-btn class="mt-4" color="primary" @click="submitImage" :disabled="!selectedFile || loading"
              :loading="loading">
              Enviar
            </v-btn>

            <v-alert type="error" class="mt-4" v-if="error">
              {{ error }}
            </v-alert>

            <v-row class="mt-4" v-if="lastResult">
              <v-col cols="6">
                <h4>Imagem original</h4>
                <v-img :src="lastResult.original" max-width="100%" />
              </v-col>
              <v-col cols="6">
                <h4>Segmentação</h4>
                <v-img :src="`data:image/png;base64,${lastResult.mask}`" max-width="100%" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios"

export default {
  data() {
    return {
      selectedFile: null,
      results: [],
      selectedDate: new Date().toISOString().substr(0, 10), // YYYY-MM-DD
      loading: false,
      error: null
    }
  },
  computed: {
    lastResult() {
      return this.results.length ? this.results[this.results.length - 1] : null
    }
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0]
      this.selectedDate = new Date().toISOString().substr(0, 10)
      this.error = null
      this.results = []  // limpa o resultado anterior
    },

    clearSelectedFile() {
      this.selectedFile = null
    },
    async toBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result)
        reader.onerror = error => reject(error)
      })
    },

    async submitImage() {
      if (!this.selectedFile) return
      this.loading = true
      this.error = null

      try {
        const buffer = await this.selectedFile.arrayBuffer()
        const base64Original = await this.toBase64(this.selectedFile)

        const response = await axios.post("http://localhost:5000/predict", buffer, {
          headers: {
            "Content-Type": "application/octet-stream"
          }
        })

        const maskBase64 = response.data.mask_base64
        const area = response.data.area

        // Salvar localmente para exibição
        const item = {
          name: this.selectedFile.name,
          original: base64Original,
          mask: maskBase64,
          area: area,
          data: this.selectedDate
        }
        console.log(item)
        this.results.push(item)

        // Enviar para o backend
        await axios.post("http://localhost:5000/segmentations", item)

      } catch (e) {
        console.error("Erro ao enviar imagem:", e)
        this.error = "Erro ao enviar imagem."
      } finally {
        this.loading = false
        this.selectedFile = null
      }
    }
  }
}
</script>
