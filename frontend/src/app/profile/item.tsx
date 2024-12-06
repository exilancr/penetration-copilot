import Link from "next/link";


export default function Item(props: any) {
    console.log('Item data:', props, props.key, props.value)
    let data = props.value;
    let title = data.title;
    let description = data.description;
    return (
        <div>
            <Link href={'/profile/'+props.key}><h1>{title}</h1></Link>
            <p>{description}</p>
        </div>
    )
}