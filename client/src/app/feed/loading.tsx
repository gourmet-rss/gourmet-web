export default function Loading() {
  return (
    <div className="flex flex-col w-full gap-4">
      {new Array(12).fill(null).map((_, i) => (
        <div key={i} className="skeleton w-full h-[100px]"></div>
      ))}
    </div>
  );
}
