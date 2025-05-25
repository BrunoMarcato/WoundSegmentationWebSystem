import { createRouter, createWebHistory } from 'vue-router'
import InferenceForm from '../components/InferenceForm.vue'
import GroupingView from '../views/GroupingView.vue'

const routes = [
  { path: '/', redirect: '/inference' },
  { path: '/inference', component: InferenceForm },
  { path: '/grouping', component: GroupingView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
