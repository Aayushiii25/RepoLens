interface MarkdownViewerProps {
  content: string
}

export function MarkdownViewer({ content }: MarkdownViewerProps) {
  return (
    <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
      {/* In a real app, use react-markdown or similar */}
      <pre className="whitespace-pre-wrap font-sans bg-transparent p-0 m-0">
        {content}
      </pre>
    </div>
  )
}
