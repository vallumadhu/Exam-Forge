import Sidebar from "./sidebar"
import FileUpload from "./fileupload"
import PromptBox from "./PromptBox"
function App() {
  return (
    <>
      <div className="layout">

        <Sidebar />

        <main className="main-layout">
          <header className="main-layout-header">Workspace</header>
          <section className="upload-section">
            <FileUpload title="Upload Notes Here" />
            <FileUpload title="Upload Questions Here" />
          </section>
          <section className="prompt-section">
            <PromptBox />
          </section>
        </main>

      </div>
    </>
  )
}

export default App