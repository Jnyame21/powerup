import { defineStore } from "pinia";


interface states {
  overlayMessage: string;
  overlayMessageColor: any;
  drawer: boolean;
  navDrawer: boolean;
  onDesk: boolean;
  activePage: string;
  errorMessage: boolean;
  deleteFunction: any;
  deleteOverlayMessage: string;
  btnSize1: string;
  btnSize2: string;
  pusherState: string;
}

export const useElementsStore = defineStore('elementsStore', {
  state: (): states =>{
    return{
      overlayMessage: '',
      overlayMessageColor: null,
      drawer: false,
      navDrawer: false,
      onDesk: false,
      activePage: '',
      errorMessage: false,
      deleteFunction: null,
      deleteOverlayMessage: '',
      btnSize1: 'x-small',
      btnSize2: 'small',
      pusherState: '',
    }
  },

  actions: {

    resetStore(){
      this.overlayMessage = ''
      this.overlayMessageColor = null
      this.drawer = false
      this.navDrawer = false
      this.activePage = ''
      this.errorMessage = false
      this.deleteFunction = null
      this.deleteOverlayMessage = ''
      this.pusherState = ''
    },

    copyToClipboard(text:string) {
      navigator.clipboard.writeText(text)
        .then(() => alert("Text Copied!"))
    },

    ShowOverlay(message: string, messageColor: any){
      const overlay = document.getElementById('AlertOverlay')
      if (overlay){
        this.overlayMessage = message
        this.overlayMessageColor = messageColor
        overlay.style.display = 'flex'
      }
    },

    ShowLoadingOverlay(){
      const overlay = document.getElementById('LoadingOverlay')
      if (overlay){
        overlay.style.display = 'flex'
      }
    },

    HideLoadingOverlay(){
      const overlay = document.getElementById('LoadingOverlay')
      if (overlay){
        overlay.style.display = 'none'
      }
    },

    ShowDeletionOverlay(func:any, message:string){
      const overlay = document.getElementById('deleteOverlay')
      this.deleteFunction = func
      this.deleteOverlayMessage = message
      if (overlay){
        overlay.style.display = 'flex'
      }
    },
  }
})

